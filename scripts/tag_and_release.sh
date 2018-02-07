#!/bin/bash
setup_env(){
    set -ex
    export YEAR=$(date +"%Y")
    export MONTH=$(date +"%m")
    export VERSION_NO=`cat VERSION`
    export APP_NAME=$(basename $(git rev-parse --show-toplevel))
    export GIT_TAG=$APP_NAME-$VERSION_NO
}

setup_git() {
    git config --global user.email "builds@travis-ci.com"
    git config --global user.name "Travis CI"
    git config --global push.default simple
}

git_tag(){
    msg="Tag Generated from TravisCI on branch $TRAVIS_BRANCH for build $TRAVIS_BUILD_NUMBER ($YEAR-$MONTH)"
    echo $msg
    echo $GIT_TAG

    git tag $GIT_TAG -a -m "$msg"
    git push origin $TRAVIS_BRANCH && git push origin $TRAVIS_BRANCH --tags
}

# invoke steps
setup_env
setup_git
git_tag
