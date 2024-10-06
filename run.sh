#!/bin/bash

docker run --network host -v "$(pwd)":/app nasa_app
