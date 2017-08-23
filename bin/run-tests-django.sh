#!/bin/bash
set -o errexit
set -o pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.inc"

cd "$PROJECT_DIR"

./manage.py test "$@"
