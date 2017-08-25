#!/bin/bash -e
set -o pipefail
echo "Installing packages..."
echo
#yarn remove eslint-config-alliance
yarn add --dev \
	git+ssh://git@gitlab.internal.alliancesoftware.com.au/alliance/eslint-config-react.git
yarn add \
	git+ssh://git@gitlab.internal.alliancesoftware.com.au/alliance/alliance-react \
	git+ssh://git@gitlab.internal.alliancesoftware.com.au/alliance/alliance-redux-api \
	react-hot-loader@3.0.0-beta.6 \
	redux-devtools-log-monitor \
	redux-devtools \
	redux-devtools-dock-monitor \
	invariant \
	react \
	react-bootstrap \
	react-dom \
	redux \
	redux-api-middleware \
	react-redux \
	history \
	react-router \
	react-router-dom \
	react-router-redux@next \
	redux-thunk \
	immutable \
	typed-immutable \
	whatwg-fetch
# Remove non-react project entry point
rm -rf ./src

[[ $(uname) =~ Darwin$ ]] && is_osx=true || is_osx=false

echo "Updating webpack project config..."
echo
if grep "\/\/ insert project-specific settings here" webpack.project.config.js > /dev/null ; then
	if $is_osx; then
		sed -i '' 's/\/\/ insert project-specific settings here/react: true,/' webpack.project.config.js
	else
		sed -i 's/\/\/ insert project-specific settings here/react: true,/' webpack.project.config.js
	fi

else
    echo "Failed to update webpack.project.config.js. Edit this manually and specify 'react' as true."
    echo
fi

echo "Updating eslint script..."
echo
if $is_osx; then
	sed -i '' 's/eslint src/eslint src-react/' package.json
else
	sed -i 's/eslint src/eslint src-react/' package.json
fi

cat > .eslintrc <<- EOM
{
  "parser": "babel-eslint",
  "extends" : [
    "react-alliance"
  ],
  "globals" : {
    "__DEBUG__"    : false,
    "__DEBUG_NEW_WINDOW__" : false,
  },
  "env"     : {
    "browser": true
  }
}
EOM
