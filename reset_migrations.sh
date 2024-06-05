#!/usr/bin/env bash

rm -rf migrations/*
rm -rf instance/*

flask --app sip_pdb db init
flask --app sip_pdb db migrate -m "inisial"
flask --app sip_pdb db upgrade