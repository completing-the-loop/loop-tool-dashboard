#!/bin/bash -e
set -o pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.inc"

nc -z localhost 8000 || fail "django server not running"

if ${CI-false} ; then
	# check that preliminary CI scripts have run
	[[ -e $frontend_dir/dist/prod/webpack-stats.json ]] || fail "Can't find prod webpack-stats.json; did you run webpack production build?"

	[[ -e $static_dir/dist/prod/webpack-stats.json ]] || fail "Can't find webpack-stats.json in static assets dir; did you collectstatic?"

	[[ $SELENIUM__STANDALONE_CHROME_PORT != "" ]] || fail "No selenium env vars; did you include the selenium service?"
	host_port=${SELENIUM__STANDALONE_CHROME_PORT##tcp://}
	nc -z ${host_port%:*} ${host_port#*:} || fail "cannot connect to selenium service at $SELENIUM__STANDALONE_CHROME_PORT"
else
	# running on dev; check for local servers to be running
	nc -z localhost 3011 || fail "webpack server not running"
	nc -z localhost 4444 || fail "selenium server not running"
fi

cd test-e2e && yarn run test -- "$@"

