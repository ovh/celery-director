#!/bin/bash
DIRECTOR_HOME=${DIRECTOR_HOME:-/app/workflows}
DIRECTOR_GIT_WORKFLOWS=${DIRECTOR_GIT_WORKFLOWS:-}
OVERIDE_DIRECTOR_ENV=${OVERIDE_DIRECTOR_ENV:-true}
export DIRECTOR_HOME

# init from a git repository if DIRECTOR_GIT_WORKFLOWS is set
if [[ ! -d "$DIRECTOR_HOME/tasks" && ! -f "$DIRECTOR_HOME/workflows.yml" ]]; then
  echo "Project not initialized !"
  if [ ! $DIRECTOR_GIT_WORKFLOWS == '' ]; then
    echo "Project initilization from git"
    mkdir -p $DIRECTOR_HOME
    echo "cloning $DIRECTOR_GIT_WORKFLOWS to $DIRECTOR_HOME"
    git clone $DIRECTOR_GIT_WORKFLOWS $DIRECTOR_HOME
  else
    echo "Project initialization"
    director init "$DIRECTOR_HOME"
  fi
else
  echo "Project already initialized"
fi
if [ -f "$DIRECTOR_HOME/requirements.txt" ]; then
  pip install -r $DIRECTOR_HOME/requirements.txt || echo ""
fi

# Overide some DIRECTOR_ENV if declared as DOCKER_DIRECTOR
if [ "$OVERIDE_DIRECTOR_ENV" = true ]; then
  source $DIRECTOR_HOME/.env || echo ""
  export $(printenv | grep ^DOCKER_DIRECTOR | sed -e "s/^DOCKER_DIRECTOR/DIRECTOR/g")
  printenv | grep ^DIRECTOR > $DIRECTOR_HOME/.env
fi

echo "Starting Director"
director "$@"