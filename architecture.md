# NOTES ON THE TODOS

I don't know how you guys wanto to handle communication between the client and the client-side engine, or if it's even worth mentioning.

I don't know what format the engine messages are in, ben, if you could write that up and put it somewhere I would appreciate it.

I don't know what format the schema should be in. SQL, I presume, but I don't know the specifics of oracle. The last project I worked on used SQLite, where we had a schema file (consisting of plain SQL) which the installation process created a new database with. In that case, the schema is in a human-readable-enough format, and it can be linked to here.

Dr. Song says he wants a "design spec", a "requirements spec", and a "testing spec". I think the design and requirement specs are supposed to be kind of like 'user experience / end result of the application' and 'inner workings / architecture of the system', respectively. This is somewhat intended to be the requirements spec. I don't know what format he wants it in though. I would like to just link him to this file. If he wants a pdf though, we may have to put it through some 'markdown to pdf' converter, and add the other files (`api.md`, db schema, etc.) as appendices.

# About

This file describes each component of the system, and how they communicate.

# HTTP Server

No implementation of this component is provided in this repository. It can be any standard HTTP server. It must be configured to serve the frontend pages.

## Links

The HTTP server serves the client to the users' browsers.

# Client

The client is implemented in the frontend repository. It runs on the users' machines in a browser. It is implemented in HTML / typescript (transpiled to javascript).

## Links

The client is served by the HTTP server.

The client communicates with the central application server via websockets to send and receive events. The specifics can be found in the backend repository, in the file `api.md`.

The client communicates with the client-side engine via **TODO**.

# Engine

The engine is implemented in the engine repository. It is implemented in c++, and is compiled to run natively and via WASM. These are referred to as the server-side engine and client-side engine, respectively. It handles the game logic for a single game: piece locations, potential piece moves, etc.

## Links

The client-side engine communicates with the client via **TODO**.

The server-side engine communicates with the central application server via POSIX pipes. The specifics can be found in **TODO**.

# Database

The database is runs on Oracle Database. It stores user data and game history. The schema can be found in the backend repository, in the file **TODO**.

## Links

The database communicates with the central application server via SQL.

# Central Application Server

The central application server (or just "the server") is implemented in the backend repository. It is implemented in python. It handles coordinating all the other components, and keeps track of in-progress games.

## Links

The server communicates with the client via websockets to send and receive events. The specifics can be found in the backend repository, in the file `api.md`.

The server communicates with the engine via POSIX pipes. The specifics can be found in **TODO**.

The server communicates with the database via SQL. The schema can me found in the backend repository, in the file **TODO**.
