"use strict";

const path = require("node:path");

const PLUGIN_ID = "authbench-policy-guard";
const PATH_RESOLUTION_ROOT = normalizeDirectory(
  process.env.AUTHBENCH_POLICY_PROJECT_ROOT || process.cwd() || "/app",
);
const FILE_PATH_KEYS = ["path", "file_path"];

function normalizeDirectory(value) {
  const raw = String(value || "").trim().replace(/\\/g, "/");
  if (!raw) {
    return "";
  }
  if (raw === "/") {
    return "/";
  }
  return raw.replace(/\/+$/, "");
}

function readString(params, keys) {
  if (!params || typeof params !== "object") {
    return null;
  }
  for (const key of keys) {
    const raw = params[key];
    if (typeof raw !== "string") {
      continue;
    }
    const value = raw.trim();
    if (value) {
      return value;
    }
  }
  return null;
}

function readStringList(params, keys) {
  if (!params || typeof params !== "object") {
    return [];
  }

  const values = [];
  const seen = new Set();
  const add = (value) => {
    const normalized = String(value || "").trim();
    if (!normalized || seen.has(normalized)) {
      return;
    }
    seen.add(normalized);
    values.push(normalized);
  };

  for (const key of keys) {
    if (!(key in params)) {
      continue;
    }
    collectStringValues(params[key], add);
  }
  return values;
}

function collectStringValues(value, add) {
  if (typeof value === "string") {
    add(value);
    return;
  }
  if (!Array.isArray(value)) {
    return;
  }
  for (const item of value) {
    if (typeof item === "string") {
      add(item);
    }
  }
}

function normalizePolicy(pluginConfig) {
  const root = pluginConfig && typeof pluginConfig === "object" ? pluginConfig : {};
  return {
    read: normalizeStringPatterns(root.read),
    write: normalizeStringPatterns(root.write),
    execute: normalizeStringPatterns(root.execute),
  };
}

function normalizeStringPatterns(value) {
  if (!Array.isArray(value)) {
    return [];
  }

  const normalized = [];
  const seen = new Set();
  for (const raw of value) {
    if (typeof raw !== "string") {
      continue;
    }
    const pattern = raw.trim();
    if (!pattern || seen.has(pattern)) {
      continue;
    }
    seen.add(pattern);
    normalized.push(pattern);
  }

  return normalized;
}

function globToRegex(pattern, slashSensitive) {
  const escaped = [];
  let i = 0;
  while (i < pattern.length) {
    const ch = pattern[i];
    if (ch === "*") {
      if (i + 1 < pattern.length && pattern[i + 1] === "*") {
        escaped.push(".*");
        i += 2;
        continue;
      }
      escaped.push(slashSensitive ? "[^/]*" : ".*");
      i += 1;
      continue;
    }
    if (ch === "?") {
      escaped.push(".");
      i += 1;
      continue;
    }
    if ("\\^$.*+?()[]{}|".includes(ch)) {
      escaped.push(`\\${ch}`);
    } else {
      escaped.push(ch);
    }
    i += 1;
  }
  return new RegExp(`^${escaped.join("")}$`);
}

const globCache = new Map();

function matchGlob(pattern, value, slashSensitive) {
  const key = `${slashSensitive ? "1" : "0"}:${pattern}`;
  let compiled = globCache.get(key);
  if (!compiled) {
    compiled = globToRegex(pattern, slashSensitive);
    globCache.set(key, compiled);
  }
  return compiled.test(value);
}

function isAbsolutePosixPath(value) {
  return String(value || "").startsWith("/");
}

function resolvePathSpecifier(pathValue) {
  const raw = String(pathValue || "").trim();
  if (!raw) {
    return null;
  }

  const normalized = raw.replace(/\\/g, "/");
  if (isAbsolutePosixPath(normalized)) {
    return path.posix.resolve(normalized);
  }
  if (!PATH_RESOLUTION_ROOT) {
    return null;
  }
  return path.posix.resolve(PATH_RESOLUTION_ROOT, normalized);
}

function normalizePathPattern(pattern) {
  const raw = String(pattern || "").trim().replace(/\\/g, "/");
  if (!raw) {
    return "";
  }
  if (raw.startsWith("./")) {
    return raw.slice(2);
  }
  return raw;
}

function matchPath(patterns, pathValue) {
  const resolvedPath = resolvePathSpecifier(pathValue);
  if (!resolvedPath) {
    return false;
  }

  return patterns.some((pattern) => {
    const normalizedPattern = normalizePathPattern(pattern);
    if (!normalizedPattern) {
      return false;
    }
    return matchGlob(normalizedPattern, resolvedPath, true);
  });
}

function evaluatePathTool(patterns, params, toolName) {
  const specifiers = readStringList(params, FILE_PATH_KEYS);

  if (specifiers.length === 0) {
    return {
      ok: false,
      reason: `policy denies ${toolName}: missing required argument`,
    };
  }

  const denied = specifiers.find((specifier) => !matchPath(patterns, specifier));
  if (denied) {
    const resolvedDenied = resolvePathSpecifier(denied);
    return {
      ok: false,
      reason: `policy denies ${toolName}: ${sanitizeBlockDetail(resolvedDenied || denied)}`,
    };
  }

  return { ok: true };
}

function sanitizeBlockDetail(value) {
  const text = String(value || "").trim();
  if (!text) {
    return "";
  }
  return text.length <= 220 ? text : `${text.slice(0, 220)}...`;
}

module.exports = {
  id: PLUGIN_ID,
  name: "AuthBench Policy Guard",
  description: "Block OpenClaw file tools that violate Authorization-Bench file permissions.",
  configSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      read: { type: "array", items: { type: "string" } },
      write: { type: "array", items: { type: "string" } },
      execute: { type: "array", items: { type: "string" } },
    },
    required: ["read", "write", "execute"],
  },
  register(api) {
    const policy = normalizePolicy(api.pluginConfig);

    api.on("before_tool_call", async (event) => {
      const toolName = String(event && event.toolName ? event.toolName : "")
        .trim()
        .toLowerCase();
      const params =
        event && event.params && typeof event.params === "object" ? event.params : {};

      if (toolName === "read") {
        if (policy.read.length === 0) {
          return {
            block: true,
            blockReason: "policy denies read: category read disabled",
          };
        }
        const verdict = evaluatePathTool(policy.read, params, toolName);
        if (!verdict.ok) {
          return {
            block: true,
            blockReason: verdict.reason,
          };
        }
        return;
      }

      if (toolName === "edit" || toolName === "write") {
        if (policy.write.length === 0) {
          return {
            block: true,
            blockReason: `policy denies ${toolName}: category write disabled`,
          };
        }
        const verdict = evaluatePathTool(policy.write, params, toolName);
        if (!verdict.ok) {
          return {
            block: true,
            blockReason: verdict.reason,
          };
        }
      }
    });
  },
};
