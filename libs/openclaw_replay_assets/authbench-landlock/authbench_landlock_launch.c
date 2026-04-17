#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <linux/landlock.h>
#include <linux/prctl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef LANDLOCK_CREATE_RULESET_VERSION
#define LANDLOCK_CREATE_RULESET_VERSION 0x00000001
#endif

#ifndef LANDLOCK_ACCESS_FS_REFER
#define LANDLOCK_ACCESS_FS_REFER (1ULL << 13)
#endif

#ifndef LANDLOCK_ACCESS_FS_TRUNCATE
#define LANDLOCK_ACCESS_FS_TRUNCATE (1ULL << 14)
#endif

typedef struct {
    char *path;
    __u64 access;
} RuleSpec;

static const __u64 READ_ACCESS =
    LANDLOCK_ACCESS_FS_READ_FILE |
    LANDLOCK_ACCESS_FS_READ_DIR;

static const __u64 WRITE_ACCESS =
    LANDLOCK_ACCESS_FS_READ_DIR |
    LANDLOCK_ACCESS_FS_WRITE_FILE |
    LANDLOCK_ACCESS_FS_REMOVE_DIR |
    LANDLOCK_ACCESS_FS_REMOVE_FILE |
    LANDLOCK_ACCESS_FS_MAKE_CHAR |
    LANDLOCK_ACCESS_FS_MAKE_DIR |
    LANDLOCK_ACCESS_FS_MAKE_REG |
    LANDLOCK_ACCESS_FS_MAKE_SOCK |
    LANDLOCK_ACCESS_FS_MAKE_FIFO |
    LANDLOCK_ACCESS_FS_MAKE_BLOCK |
    LANDLOCK_ACCESS_FS_MAKE_SYM |
    LANDLOCK_ACCESS_FS_REFER |
    LANDLOCK_ACCESS_FS_TRUNCATE;

static const __u64 EXECUTE_ACCESS = LANDLOCK_ACCESS_FS_EXECUTE;

static int landlock_create_ruleset_wrapper(
    const struct landlock_ruleset_attr *attr,
    size_t size,
    __u32 flags
) {
    return syscall(__NR_landlock_create_ruleset, attr, size, flags);
}

static int landlock_add_rule_wrapper(
    int ruleset_fd,
    enum landlock_rule_type rule_type,
    const void *rule_attr,
    __u32 flags
) {
    return syscall(__NR_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags);
}

static int landlock_restrict_self_wrapper(int ruleset_fd, __u32 flags) {
    return syscall(__NR_landlock_restrict_self, ruleset_fd, flags);
}

static void die(const char *message) {
    fprintf(stderr, "%s\n", message);
    exit(1);
}

static void die_errno(const char *label) {
    fprintf(stderr, "%s failed: %s\n", label, strerror(errno));
    exit(1);
}

static char *xstrdup(const char *value) {
    char *copy = strdup(value);
    if (copy == NULL) {
        die_errno("strdup");
    }
    return copy;
}

static char *normalize_exact_path(const char *raw_path) {
    if (raw_path == NULL || raw_path[0] != '/') {
        die("Landlock paths must be absolute POSIX paths.");
    }

    char *working = xstrdup(raw_path);
    size_t read_index = 0;
    size_t write_index = 0;

    while (working[read_index] != '\0') {
        char current = working[read_index++];
        if (current != '/') {
            working[write_index++] = current;
            continue;
        }
        working[write_index++] = '/';
        while (working[read_index] == '/') {
            read_index += 1;
        }
    }
    working[write_index] = '\0';

    while (write_index > 1 && working[write_index - 1] == '/') {
        working[--write_index] = '\0';
    }
    return working;
}

static char *parent_directory_path(const char *raw_path) {
    char *path = normalize_exact_path(raw_path);
    char *last_slash = strrchr(path, '/');
    if (last_slash == NULL) {
        die("Landlock paths must be absolute POSIX paths.");
    }
    if (last_slash == path) {
        path[1] = '\0';
        return path;
    }
    *last_slash = '\0';
    return path;
}

static bool path_exists(const char *path) {
    struct stat st;
    return stat(path, &st) == 0;
}

static bool path_is_directory(const char *path) {
    struct stat st;
    if (stat(path, &st) != 0) {
        return false;
    }
    return S_ISDIR(st.st_mode);
}

static char *closest_existing_ancestor_directory(const char *raw_path) {
    char *current = normalize_exact_path(raw_path);
    while (true) {
        if (path_exists(current) && path_is_directory(current)) {
            if (strcmp(current, "/") == 0) {
                free(current);
                return NULL;
            }
            return current;
        }

        char *parent = parent_directory_path(current);
        free(current);
        current = parent;
        if (strcmp(current, "/") == 0) {
            free(current);
            return NULL;
        }
    }
}

static void add_or_merge_rule(RuleSpec *rules, size_t *count, const char *raw_path, __u64 access) {
    char *path = normalize_exact_path(raw_path);
    for (size_t index = 0; index < *count; index += 1) {
        if (strcmp(rules[index].path, path) == 0) {
            rules[index].access |= access;
            free(path);
            return;
        }
    }

    rules[*count].path = path;
    rules[*count].access = access;
    *count += 1;
}

static void add_rule_from_arg(RuleSpec *rules, size_t *count, const char *raw_spec, __u64 access) {
    size_t length = strlen(raw_spec);
    if (length >= 3 && strcmp(raw_spec + length - 3, "/**") == 0) {
        char *base = xstrdup(raw_spec);
        base[length - 3] = '\0';
        if (access == WRITE_ACCESS && !path_exists(base)) {
            char *ancestor = closest_existing_ancestor_directory(base);
            if (ancestor != NULL) {
                add_or_merge_rule(rules, count, ancestor, access);
                free(ancestor);
            }
            free(base);
            return;
        }
        if ((access == READ_ACCESS || access == EXECUTE_ACCESS) && !path_exists(base)) {
            free(base);
            return;
        }
        add_or_merge_rule(rules, count, base, access);
        free(base);
        return;
    }
    if (access == WRITE_ACCESS) {
        char *parent = parent_directory_path(raw_spec);
        if (!path_exists(parent)) {
            char *ancestor = closest_existing_ancestor_directory(parent);
            if (ancestor != NULL) {
                add_or_merge_rule(rules, count, ancestor, access);
                free(ancestor);
            }
            free(parent);
            return;
        }
        add_or_merge_rule(rules, count, parent, access);
        free(parent);
        return;
    }
    if (access == READ_ACCESS) {
        char *path = normalize_exact_path(raw_spec);
        if (!path_exists(path)) {
            char *ancestor = closest_existing_ancestor_directory(path);
            if (ancestor != NULL) {
                add_or_merge_rule(rules, count, ancestor, READ_ACCESS);
                free(ancestor);
            }
            free(path);
            return;
        }
        if (path_is_directory(path)) {
            add_or_merge_rule(rules, count, path, READ_ACCESS);
        } else {
            add_or_merge_rule(rules, count, path, LANDLOCK_ACCESS_FS_READ_FILE);
        }
        free(path);
        return;
    }
    if (access == EXECUTE_ACCESS) {
        if (!path_exists(raw_spec)) {
            return;
        }
        add_or_merge_rule(rules, count, raw_spec, EXECUTE_ACCESS);
        return;
    }
    add_or_merge_rule(rules, count, raw_spec, access);
}

static void install_rule(int ruleset_fd, const RuleSpec *rule) {
    int path_fd = open(rule->path, O_PATH | O_CLOEXEC);
    if (path_fd < 0) {
        die_errno(rule->path);
    }

    struct landlock_path_beneath_attr attr = {
        .allowed_access = rule->access,
        .parent_fd = path_fd,
    };
    if (landlock_add_rule_wrapper(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &attr, 0) != 0) {
        close(path_fd);
        die_errno("landlock_add_rule");
    }
    close(path_fd);
}

int main(int argc, char **argv) {
    RuleSpec *rules = calloc((size_t)argc, sizeof(RuleSpec));
    if (rules == NULL) {
        die_errno("calloc");
    }

    size_t rule_count = 0;
    int command_index = -1;
    for (int index = 1; index < argc; index += 1) {
        const char *arg = argv[index];
        if (strcmp(arg, "--") == 0) {
            command_index = index + 1;
            break;
        }
        if (index + 1 >= argc) {
            die("Landlock launcher option requires a value.");
        }
        if (strcmp(arg, "--read") == 0) {
            add_rule_from_arg(rules, &rule_count, argv[index + 1], READ_ACCESS);
            index += 1;
            continue;
        }
        if (strcmp(arg, "--write") == 0) {
            add_rule_from_arg(rules, &rule_count, argv[index + 1], WRITE_ACCESS);
            index += 1;
            continue;
        }
        if (strcmp(arg, "--execute") == 0) {
            add_rule_from_arg(rules, &rule_count, argv[index + 1], EXECUTE_ACCESS);
            index += 1;
            continue;
        }
        die("Unsupported Landlock launcher option.");
    }

    if (command_index < 0 || command_index >= argc) {
        die("Landlock launcher requires a command after --.");
    }

    int abi = landlock_create_ruleset_wrapper(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        die_errno("landlock ABI query");
    }

    struct landlock_ruleset_attr ruleset_attr = {
        .handled_access_fs = READ_ACCESS | WRITE_ACCESS | EXECUTE_ACCESS,
    };
    int ruleset_fd = landlock_create_ruleset_wrapper(&ruleset_attr, sizeof(ruleset_attr), 0);
    if (ruleset_fd < 0) {
        die_errno("landlock_create_ruleset");
    }

    for (size_t index = 0; index < rule_count; index += 1) {
        install_rule(ruleset_fd, &rules[index]);
    }

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        die_errno("prctl(PR_SET_NO_NEW_PRIVS)");
    }
    if (landlock_restrict_self_wrapper(ruleset_fd, 0) != 0) {
        die_errno("landlock_restrict_self");
    }
    close(ruleset_fd);

    execvp(argv[command_index], &argv[command_index]);
    die_errno("execvp");
    return 1;
}
