# This is a wrapper to bin/common.inc for git hooks
#
# git hooks in our dir structure hooks are executed through a symlink;
# we can't use realpath() from common.inc because we don't know how to find it!
realpath=$( command -v realpath >/dev/null 2>&1 ) || function realpath() {
	python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1"
}
self_path=$( realpath $(dirname "${BASH_SOURCE[0]}") )
source "$self_path/../bin/common.inc"

commit_categories='build|docs|feat|fix|refactor|style|sys|test|WIP'
commit_categories_bare='build|WIP'

