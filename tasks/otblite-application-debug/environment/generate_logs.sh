#!/bin/bash

set -eu

LOG_LEVELS=("FATAL" "ERROR" "WARN" "INFO" "DEBUG")
EXCEPTIONS=(
  "java.lang.NullPointerException"
  "java.io.IOException"
  "java.sql.SQLException"
  "java.lang.IllegalArgumentException"
  "java.util.concurrent.TimeoutException"
  "java.net.ConnectException"
  "java.lang.OutOfMemoryError"
  "java.lang.ClassNotFoundException"
  "java.security.AccessControlException"
  "javax.servlet.ServletException"
)
LOG_FILES=(
  "app_78uitx.log"
  "app_e2sg29.log"
  "app_e6063g.log"
  "app_mqdggg.log"
  "app_sxooxg.log"
)

mkdir -p /app/logs

for LOG_NAME in "${LOG_FILES[@]}"; do
  LOGFILE="/app/logs/${LOG_NAME}"
  NUM_ENTRIES=$((50 + RANDOM % 101))

  for j in $(seq 1 "$NUM_ENTRIES"); do
    MONTH=$(printf "%02d" $((1 + RANDOM % 12)))
    DAY=$(printf "%02d" $((1 + RANDOM % 28)))
    HOUR=$(printf "%02d" $((RANDOM % 24)))
    MIN=$(printf "%02d" $((RANDOM % 60)))
    SEC=$(printf "%02d" $((RANDOM % 60)))
    TIMESTAMP="2024-${MONTH}-${DAY} ${HOUR}:${MIN}:${SEC}"

    LEVEL_RAND=$((RANDOM % 100))
    if [ "$LEVEL_RAND" -lt 15 ]; then
      LEVEL="FATAL"
    elif [ "$LEVEL_RAND" -lt 40 ]; then
      LEVEL="ERROR"
    elif [ "$LEVEL_RAND" -lt 65 ]; then
      LEVEL="WARN"
    elif [ "$LEVEL_RAND" -lt 85 ]; then
      LEVEL="INFO"
    else
      LEVEL="DEBUG"
    fi

    EXCEPTION="${EXCEPTIONS[$((RANDOM % ${#EXCEPTIONS[@]}))]}"
    CLASS_NAME="com.example.app.Service$((RANDOM % 10))"
    LINE_NUM=$((10 + RANDOM % 500))

    if [[ "$LEVEL" == "ERROR" || "$LEVEL" == "FATAL" ]]; then
      echo "$TIMESTAMP [$LEVEL] $CLASS_NAME - Exception occurred: $EXCEPTION" >> "$LOGFILE"
      echo "    at $CLASS_NAME.method$((RANDOM % 5))($CLASS_NAME.java:$LINE_NUM)" >> "$LOGFILE"
      echo "    at com.example.app.Controller.handle(Controller.java:$((RANDOM % 100)))" >> "$LOGFILE"
      echo "    at javax.servlet.http.HttpServlet.service(HttpServlet.java:$((RANDOM % 200)))" >> "$LOGFILE"
    else
      echo "$TIMESTAMP [$LEVEL] $CLASS_NAME - Processing request #$((RANDOM % 1000))" >> "$LOGFILE"
    fi
  done
done

echo "Generated ${#LOG_FILES[@]} log files with Java application logs"
