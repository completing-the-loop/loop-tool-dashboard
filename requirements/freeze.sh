#!/bin/bash -e
set -o pipefail

PIP="pip"

[[ ! -e freeze.default ]] || DEFAULT_REQUIREMENTS=`cat freeze.default`
DEFAULT_REQUIREMENTS=${DEFAULT_REQUIREMENTS:-prod.txt}

help() {
	echo "Syntax: $0 [env.txt]"
	echo
	echo Current virtualenv must already exist
	exit 1
}

[[ $# -le 2 ]] || help
REQUIREMENTS_IN="${1:-$DEFAULT_REQUIREMENTS}"

[[ -e "$VIRTUAL_ENV" ]] || ( echo "Missing VIRTUAL_ENV (you need to activate a virtualenv first; try 'workon')" 2>&1 ; exit 1)

# Parse arguments
while [[ $# > 0 ]] ; do
	case "$1" in
		# currently disabled because autodetect should work now and we want to ensure uses the same binary as is in the virtualenv
		--python=*)
			#PYTHON_BIN=${1#*=}
			;;
		--python)
			#PYTHON_BIN="$2"
			shift
			;;
		*)
			REQUIREMENTS_IN="$1"
			;;
	esac
	shift
done

REQUIREMENTS_OUT="requirements.txt"

# If not specified, use the current python binary
# We have to resolve it to the system python binary not the virtulenv binary; this seems hacky but appears to work
if [[ -z "$PYTHON_BIN" ]] ; then
	PYTHON_VER_ABC=$( python -V 2>&1 | cut -f2 -d' ' | cut -f-3 -d. )
	PYTHON_VER_AB=$(  python -V 2>&1 | cut -f2 -d' ' | cut -f-2 -d. )
	PYTHON_VER_A=$(   python -V 2>&1 | cut -f2 -d' ' | cut -f-1 -d. )
	PYTHON_BIN=`python -c "import sysconfig ; print(sysconfig.get_config_var('BINDIR'))"`
	for VER in $PYTHON_VER_ABC $PYTHON_VER_AB $PYTHON_VER_A "" ; do
		if [[ -x "$PYTHON_BIN/python$VER" ]] ; then
			PYTHON_BIN="$PYTHON_BIN/python$VER"
			break
		fi
	done
fi

# resolve symlinked python binary to actual python binary
# if passing --python= it must be to a system python binary, not to a virtualenv python binary
if [ $(uname) = 'Darwin' ] ; then
	READLINK="greadlink"
	if ! "$READLINK" -f / >/dev/null 2>/dev/null ; then
		echo "Can't find greadlink. brew install coreutils"
		exit 1
	fi
else
	READLINK="readlink"
fi
PYTHON_BIN=`"$READLINK" -f "$PYTHON_BIN"`
if [ $("$READLINK" -f "$PYTHON_BIN") = $("$READLINK" -f "$VIRTUAL_ENV/$VIRTUALENVWRAPPER_ENV_BIN_DIR/python") ] ; then
	echo "--python=... cannot refer to the python in the virtualenv" 2>&1
	exit 1
fi

PYTHON_VER=$( "${PYTHON_BIN}" -V 2>&1 | cut -f2 -d' ' | cut -f-2 -d. )
#PYTHON_VER=$( virtualenvwrapper_get_python_version )

echo "input reqs:   ${REQUIREMENTS_IN:-ERROR}"
echo "output reqs:  ${REQUIREMENTS_OUT:-ERROR}"
echo "virtualenv:   ${VIRTUAL_ENV:-ERROR}"
echo "python bin:   ${PYTHON_BIN}"
echo "python ver:   ${PYTHON_VER}"

[[ -x "$PYTHON_BIN" ]] || ( echo "Bad python binary: $PYTHON_BIN" 2>&1 ; exit 1)
[[ -e "$REQUIREMENTS_IN" ]] || ( echo "Missing pip requirements file: $REQUIREMENTS_IN" 2>&1 ; exit 1)

echo Press Enter to continue or Ctrl-C to abort
read

function resetvirtualenv() {
	local REQUIREMENTS_IN="$1"

	echo
	echo
	echo "---------------------------------------------------------------------------------"
	echo "Clearing virtualenv"
	echo "---------------------------------------------------------------------------------"

	# Can't delete & recreate easily since paths will be pointing to this and
	# we don't have access to virtualenvwrapper directly
	virtualenv --clear "$VIRTUAL_ENV" --no-setuptools "--python=$PYTHON_BIN"
	#pip freeze | grep -v '^pip=' | xargs pip uninstall -y

	echo
	echo
	echo "---------------------------------------------------------------------------------"
	echo "Upgrading to latest virtualenv"
	echo "---------------------------------------------------------------------------------"
	$PIP install --upgrade virtualenv

	echo
	echo
	echo "---------------------------------------------------------------------------------"
	echo "Installing setuptools"
	echo "---------------------------------------------------------------------------------"
	# setuptools >=34 introduces unnecessary dependencies
	$PIP install 'setuptools<34'

	echo
	echo
	echo "---------------------------------------------------------------------------------"
	echo "Upgrading to latest pip"
	echo "---------------------------------------------------------------------------------"
	$PIP install --upgrade pip

	echo
	echo
	echo "---------------------------------------------------------------------------------"
	echo "Installing requirements"
	echo "---------------------------------------------------------------------------------"
	$PIP install -r "$REQUIREMENTS_IN"
}

resetvirtualenv "$REQUIREMENTS_IN"

echo
echo
echo "---------------------------------------------------------------------------------"
echo "Saving requirements"
echo "---------------------------------------------------------------------------------"
# no -r $REQUIREMENTS_IN because pip doesn't handle includes properly
$PIP freeze | sed 's/^pytz=.*$/pytz/' | grep -E -v '^(virtualenv)([>=<]|$)' > "$REQUIREMENTS_OUT"

# If for some reason you're stuck with setuptools>=34 then you probably want to filter out the artificial dependencies
#$PIP freeze | sed 's/^pytz=.*$/pytz/' | grep -E -v '^(setuptools|appdirs|packaging|pyparsing)([>=<]|$)' > "$REQUIREMENTS_OUT"


echo
echo
echo "---------------------------------------------------------------------------------"
echo "Installing dev requirements"
echo "---------------------------------------------------------------------------------"
echo
echo "About to install dev.txt requirements"
echo
echo "Press Enter to continue or Ctrl-C to abort"
read
$PIP install -r dev.txt
