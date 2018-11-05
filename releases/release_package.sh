#! /bin/bash

set -e

#
# Setup and test parameters etc.
#

REPO='wapi-python'
VERSION=$(<VERSION)
RELEASE="v$VERSION"
PYVERSION=$(grep ^VERSION wapi/__init__.py | awk '{print $5}' | tr -d "'")
MODE="$1"

if [ "$MODE" != "test" -a "$MODE" != "release" ]; then
  echo "Mode argument must be either 'test' or 'release'"
  exit 1
fi

if [ "$VERSION" != "$PYVERSION" ]; then
  echo "Version differs in VERSION and wapi/__init__.py ($VERSION != $PYVERSION)"
  exit 1
fi

if curl -f -H "Authorization: token $GITHUB_TRAVIS_TOKEN" \
        https://api.github.com/repos/wattsight/$REPO/releases/tags/$RELEASE >/dev/null 2>&1
then
  echo "Release $RELEASE already exists, update VERSION (and wapi-python/__init__.py)"
  exit 1
fi

if [ ! -r "./releases/relnote-$VERSION" ]; then
  echo "Release note for $VERSION missing"
  exit 1
fi

if [ "$MODE" == "test" ]; then
  echo "Testing passed."
  exit 0
fi

#
# Release to github
#

echo "Release to GITHUB."
BODY_STRING=$(cat ./releases/relnote-$VERSION | sed -e 's/"/\\"/g' -e 's/$/\\n/' | tr -d '\n')
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

echo "Release to PYPI."
shippable_retry pip install -U twine
rm -rf dist
python setup.py sdist bdist_wheel
twine upload dist/wapi-python-$VERSION-*
