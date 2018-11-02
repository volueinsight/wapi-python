#! /bin/bash

set -e

#
# Setup and test parameters etc.
#

REPO='wapi-python'
VERSION=$(<VERSION)
RELEASE="v$VERSION"
MODE="$1"

if [ "$MODE" != "test" -a "$MODE" != "release" ]; then
  echo "Mode argument must be either 'test' or 'release'"
  exit 1
fi

if curl -f -H "Authorization: token $GITHUB_TRAVIS_TOKEN" \
        https://api.github.com/repos/wattsight/$REPO/releases/tags/$RELEASE
then
  echo "Release $RELEASE already exists, update VERSION (and wapi-python/__init__.py)"
  exit 1
fi

if [ ! -r "./releases/relnote-$VERSION" ]; then
  echo "Release note for $VERSION missing"
  exit 1
fi

BODY_STRING=$(cat ./releases/relnote-$VERSION | sed -e 's/"/\\"/g' -e 's/$/\\n/' | tr -d '\n')
echo "Have $BODY_STRING"

if [ "$MODE" == "test" ]; then
  echo "Testing passed."
  exit 0
fi

#
# Release to github
#

JSON_DATA="{
  \"tag_name\": \"$RELEASE\",
  \"target_commitish\": \"master\",
  \"name\": \"$RELEASE\",
  \"body\": \"$BODY_STRING\"
}"
curl -d "$JSON_DATA" -H "Authorization: token $GITHUB_TRAVIS_TOKEN" \
        https://api.github.com/repos/wattsight/$REPO/releases


#
# Release to pypi
#

echo "Release to PYPI missing, do it manually."
