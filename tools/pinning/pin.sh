#!/bin/bash
set -euo pipefail

WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
REPO_ROOT="$(dirname "$(dirname "${WORK_DIR}")")"
PIPSTRAP_CONSTRAINTS="${REPO_ROOT}/tools/pipstrap_constraints.txt"
RELATIVE_SCRIPT_PATH="$(realpath --relative-to "$REPO_ROOT" "$WORK_DIR")/$(basename "${BASH_SOURCE[0]}")"
REQUIREMENTS_FILE="$REPO_ROOT/tools/requirements.txt"
STRIP_HASHES="${REPO_ROOT}/tools/strip_hashes.py"

if ! command -v poetry >/dev/null || ! command -v hashin >/dev/null; then
    echo "Please install poetry and hashin."
    echo "You may need to recreate Certbot's virtual environment and activate it."
    exit 1
fi

cd "${WORK_DIR}"

if [ -f poetry.lock ]; then
    rm poetry.lock
fi

poetry lock

TEMP_REQUIREMENTS=$(mktemp)
trap 'rm $TEMP_REQUIREMENTS' EXIT

poetry export -o "${TEMP_REQUIREMENTS}" --without-hashes
# We need to remove local packages from the requirements file.
sed -i '/^acme @/d; /certbot/d;' "${TEMP_REQUIREMENTS}"
# Poetry currently will not include pip, setuptools, or wheel in lockfiles or
# requirements files. See https://github.com/python-poetry/poetry/issues/1584
# which should hopefully be resolved soon by
# https://github.com/python-poetry/poetry/pull/2826. For now, we continue to
# keep pipstrap's pinning separate which has the added benefit of having it
# continue to check hashes when pipstrap is run directly.
"${STRIP_HASHES}" "${PIPSTRAP_CONSTRAINTS}" >>  "${TEMP_REQUIREMENTS}"

cat << EOF > "$REQUIREMENTS_FILE"
# This file was generated by $RELATIVE_SCRIPT_PATH.
#
# It is normally used as constraints to pip, however, it has the name
# requirements.txt so that is scanned by GitHub. See
# https://docs.github.com/en/github/visualizing-repository-data-with-graphs/about-the-dependency-graph#supported-package-ecosystems
# for more info.
EOF
cat "${TEMP_REQUIREMENTS}" >> "${REQUIREMENTS_FILE}"