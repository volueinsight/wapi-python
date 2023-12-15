#! /bin/bash

# Note 15.12.23: This docker file is no more in use s
# Releases are done via Github Actions

set -e

#
# Setup and test parameters etc.
#

REPO='wapi-python'
SRCDIR='wapi'
VERSION=$(<VERSION)
RELEASE="v$VERSION"
PYVERSION=$(grep ^VERSION $SRCDIR/__init__.py | awk '{print $5}' | tr -d "'")
MODE="$1"
PYPI_INDEX="$2"
echo "PYPI_INDEX="$PYPI_INDEX

if [ "$MODE" != "test" -a "$MODE" != "release" ]; then
  echo "Mode argument must be either 'test' or 'release'"
  exit 1
fi

if [ "$PYPI_INDEX" != "testpypi" -a "$PYPI_INDEX" != "pypi" ]; then
  echo "PYPI_INDEX argument must be either 'testpypi' or 'pypi'"
  exit 1
fi

if [ "$VERSION" != "$PYVERSION" -a "$PYPI_INDEX" == "pypi" ]; then
  echo "Version differs in VERSION and $SRCDIR/__init__.py ($VERSION != $PYVERSION)"
  exit 1
fi

if [ "$PYPI_INDEX" == "pypi" -a curl -f -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/repos/volueinsight/$REPO/releases/tags/$RELEASE >/dev/null 2>&1 ]; then
  echo "Release $RELEASE already exists, update VERSION (and $SRCDIR/__init__.py)"
  exit 1
fi

if [ "$PYPI_INDEX" == "pypi" -a ! -r "./releases/relnote-$VERSION" ]; then
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

if [ "$PYPI_INDEX" == "pypi" ]; then
    echo "Release to GITHUB."
    BODY_STRING=$(cat ./releases/relnote-$VERSION | sed -e 's/"/\\"/g' -e 's/$/\\n/' | tr -d '\n')
    JSON_DATA="{
      \"tag_name\": \"$RELEASE\",
      \"target_commitish\": \"master\",
      \"name\": \"$RELEASE\",
      \"body\": \"$BODY_STRING\"
    }"
    curl -d "$JSON_DATA" -H "Authorization: token $GITHUB_TOKEN" \
            https://api.github.com/repos/volueinsight/$REPO/releases
fi

#
# Release to pypi
#

echo "Release to $PYPI_INDEX."
rm -rf dist
python setup.py sdist bdist_wheel
echo "PYPI release: setup.py completed"
twine upload --verbose --repository $PYPI_INDEX dist/wapi-python-$VERSION.tar.gz dist/wapi_python-$VERSION-*.whl

echo "Released successfully"
