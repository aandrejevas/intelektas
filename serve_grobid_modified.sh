#!/bin/bash

# download GROBID if directory does not exist
declare -r GROBID_VERSION="0.7.2" # or change to current stable version

if [ ! -d grobid-${GROBID_VERSION} ]; then
  wget --no-check-certificate https://github.com/kermitt2/grobid/archive/${GROBID_VERSION}.zip
  unzip "${GROBID_VERSION}.zip"
  rm "${GROBID_VERSION}.zip"
fi

# run GROBID

if [ -d "grobid-installation" ]; then
  echo "Running grobid-service"
  cd grobid-installation || exit
  ./grobid-service/bin/grobid-service
else
  echo "Running gradle clean assemble"
  cd grobid-${GROBID_VERSION} || exit
  ./gradlew clean assemble
  cd ..
  mkdir grobid-installation
  cd grobid-installation
  echo "Unzipping grobid-service-${GROBID_VERSION}.zip"
  unzip ../grobid-${GROBID_VERSION}/grobid-service/build/distributions/grobid-service-${GROBID_VERSION}.zip
  echo "Renaming grobid-service-${GROBID_VERSION} to grobid-service"
  mv grobid-service-${GROBID_VERSION} grobid-service
  echo "Unzipping grobid-service-${GROBID_VERSION}.zip"
  unzip ../grobid-${GROBID_VERSION}/grobid-home/build/distributions/grobid-home-${GROBID_VERSION}.zip
  pwd
  ./grobid-service/bin/grobid-service
fi

