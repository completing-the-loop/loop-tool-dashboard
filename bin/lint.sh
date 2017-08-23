#!/bin/bash -e
set -o pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.inc"

cd "$repo_dir"

return_code=0

[[ $(pwd) =~ template-django$ ]] && is_template_repo=true || is_template_repo=false

function err() {
	echo "ERROR: $1" >&2
	return_code=1
}
function warn() {
	echo "WARNING: $1" >&2
}

function lint_python_version() {
	# check python version (requirements.txt)
	# Should look something like this:
	#   python-version-3.5.3; python_version < '3.5.3' or python_version > '3.5.3'
	# or
	#   python-version-3.5; python_version < '3.5' or python_version > '3.5'
	local python_version_pip
	local python_version_pip_regex
	local python_version_pip_minor
	local python_version_pip_minor_regex
	local python_version_latest
	local python_version_active
	local python_version_pyenv
	local pyenv_regex

	local python_version_os_maintained
	python_version_os_maintained=(
		# Debian 8
		2.7.9
		3.4.2

		# Ubuntu 14.04
		2.7.6
		3.4.3

		# Ubuntu 16.04
		2.7.12
		3.5.2
	)

	python_version_pip=$( sed -E 's/^python-(assert-)?version-(([0-9]+\.)*[0-9]+).*$/\2/p;d' < requirements.txt )
	if [[ $python_version_pip = "" ]] ; then
		err "requirements.txt does not specify a python version"
	fi
	python_version_pip_regex="^${python_version_pip//./\\.}"
	python_version_pip_minor="$( sed -E 's/^python-(assert-)?version-([0-9]+\.[0-9]+).*$/\2/p;d' < requirements.txt )."
	python_version_pip_minor_regex="^${python_version_pip_minor//./\\.}"

	if $( which pyenv >/dev/null ) ; then
		# find the latest not-prerelease cpython available
		if ! python_version_latest=$( pyenv install --list | sed 's/  //' | grep -E "${python_version_pip_minor_regex}" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | tail -n 1 ) ; then
			err "Cannot determine latest python version"
		fi
		python_version_latest="${python_version_latest// /}"
	else
		python_version_latest=""
	fi

	# check python version (current environment)
	python_version_active=$( python --version 2>&1 | sed 's/Python //' )

	if [[ ! $python_version_active =~ $python_version_pip_regex ]] ; then
		if [[ $python_version_active =~ $python_version_pip_minor_regex ]] ; then
			warn "Active python version ($python_version_active) != requirements.txt ($python_version_pip)"
		else
			err  "Active python version ($python_version_active) != requirements.txt ($python_version_pip)"
		fi
	fi

	# check python version (pyenv)
	if [[ ! -e .python-version ]] ; then
		err "No pyenv .python-version specified"
	else
		python_version_pyenv="$(<.python-version)"
		python_version_pyenv="${python_version_pyenv// /}"

		if [[ ! $python_version_pyenv =~ $python_version_pip_regex ]] ; then
			err "requirements.txt ($python_version_pip) != pyenv .python-version ($python_version_pyenv)"
		fi

		if [[ $python_version_latest != "" && $python_version_pyenv != ${python_version_latest} ]] ; then
			# These versions are part of base OS distributions; security patches are backported so don't
			# warn about not being the latest version if using them (we can't tell here where the site is
			# to be deployed be this is good enough)

			pyenv_regex=" ${python_version_pyenv//./\\.} "
			if [[ ! " ${python_version_os_maintained[@]} "  =~ $python_version_pyenv_regex ]] ; then
				warn "pyenv .python-version ($python_version_pyenv) != latest point release ($python_version_latest)"
			fi
		fi
	fi

	# check python version (heroku)
	if [[ -e runtime.txt ]] ; then
		python_version_heroku="$(<runtime.txt)"
		python_version_heroku="${python_version_heroku//python-/}"

		if [[ ! $python_version_heroku =~ $python_version_pip_regex ]] ; then
			err "heroku runtime.txt ($python_version_heroku) != requirements.txt ($python_version_pip)"
		fi

		if [[ $python_version_heroku != $python_version_pyenv ]] ; then
			err "heroku runtime.txt ($python_version_heroku) != pyenv .python-version ($python_version_pyenv)"
		fi

		if [[ $python_version_latest != "" && $python_version_heroku != ${python_version_latest} ]] ; then
			err "heroku runtime.txt ($python_version_heroku) != latest point release ($python_version_latest)"
		fi
	fi
}

function lint_virtualenv() {
	# virtualenv
	if [[ ! -e .venv ]] ; then
		err "You have no .venv file"
	else
		# has the virtualenv name been changed?
		if [[ "$(<.venv)" = "alliance-template-django" ]] && ! $is_template_repo; then
			err "Virtualenv name in .venv has not been changed"
		fi

		# are we using the right virtualenv?
		if [[ ${VIRTUAL_ENV} = "" ]] ; then
			err "No virtualenv is active"
		elif [[ ${VIRTUAL_ENV##*/} != "$(<.venv)" ]] && ! $is_ci ; then
			warn "Active virtualenv (${VIRTUAL_ENV##*/}) != expected ($(<.venv)). Are you using the right virtualenv?"
		fi
	fi
}

function lint_python_packages() {
	# We use Operating System pytz to ensure timezone updates happen automatically
	if egrep '^\s*pytz[^$]' requirements/*.txt >/dev/null ; then
		err "pytz version specified in requirements - this will overwrite OS pytz. remove it."
	fi

    # TODO: Strictly speaking this only applies to the AJAX list filter
    # We could check for instances of ModelFieldSearchView or descendants instead of blacklisting the
    # whole package but the fact that this is in there at all is concerning
	if egrep '^\s*django-admin-steroids' requirements/*.txt >/dev/null ; then
	    err "django-admin-steroids use is STRONGLY discouraged. See https://github.com/chrisspen/django-admin-steroids/issues/14"
	fi
}

function lint_js() {
	# nodejs minor version number
	if [[ -e .nvmrc ]] && [[ "$(<.nvmrc)" =~ \. ]] ; then
		warn "You have specified a nodejs minor version in .nvmrc -- is this necessary?"
	fi

	# If there's a package.json then there should be a lockfile of some sort
	local package_json
	for package_json in $( find . -name package.json ! -path \*/node_modules/\* ! -path \*/bower_components/\* ! -path \*cache\* ) ; do
		if ! [[ -e ${package_json/package\.json/yarn.lock} ]] && ! [[ -e ${package_json/package\.json/npm-shrinkwrap.json} ]] && ! $is_template_repo ; then
			err "${package_json/.\//} has no yarn.lock or npm-shrinkwrap.json"
		fi
	done

	# We should have a .nvmrc if we're using node
	if $( find . -name package.json ! -path \*node_modules\* >/dev/null ) || $( find . -name yarn.lock ! -path \*node_modules\* >/dev/null ) ; then
		if ! $( find . -name .nvmrc >/dev/null ) ; then
			err "Found a package.json without any .nvmrc"
		fi
	fi

	# Keep life simple: don't put whitespace in filenames or this may fail
	local filename
	for filename in $( find . -name packages.json -maxdepth 1 ) ; do
		if grep 'TEMPLATE_FIXME' "$filename" >/dev/null && ! $is_template_repo ; then
			err "You have template data in $filename"
		fi
	done

}

function lint_doc() {
	if [[ ! -e README.md ]] ; then
		err "You have no README.md"
	elif ! $is_template_repo ; then
		if grep '# My Project' README.md >/dev/null ||
			grep 'alliance/template-django' README.md >/dev/null
		then
			err "You appear to have an unchanged README.md"
		fi
	fi

	if [[ ! -e logo.png ]] ; then
		err "Missing logo.png"
	else
		template_logo_md5="f442b9d75f10cd5ca5d6f27e624dbb39"
		if $is_template_repo ; then
			if [[ "$( $MD5SUM logo.png )" != "$template_logo_md5  logo.png" ]] ; then
				err "$0 needs to be updated with new logo.png hash"
			fi
		else
			if [[ "$( $MD5SUM logo.png )" = "$template_logo_md5  logo.png" ]] ; then
				err "logo.png has not been updated"
			fi
		fi
	fi
}


# actual source code linting
function lint_source() {
	bin/reformat-imports.sh --check-only "$@"
}

lint_python_version
lint_virtualenv
lint_python_packages
lint_js
lint_doc

lint_source

exit $return_code
