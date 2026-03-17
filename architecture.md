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

The client communicates with the client-side engine via web assembly import.

# Engine

The engine is implemented in the engine repository. It is implemented in c++, and is compiled to run natively and via WASM. These are referred to as the server-side engine and client-side engine, respectively. It handles the game logic for a single game: piece locations, potential piece moves, etc.

## Links

The client-side engine communicates with the client via web assembly import.

The server-side engine communicates with the central application server via POSIX pipes. The specifics can be found in the backend repository, in the file `engine.md`.

# Database

The database runs on MySQL 8. It stores user data and game history. Details (how to run it, schema, seed, connection) are in the backend repository in `db.md`; the schema and seed live in `db/schema.sql` and `db/seed.sql`.

## Links

The database communicates with the central application server via SQL.

# Central Application Server

The central application server (or just "the server") is implemented in the backend repository. It is implemented in python. It handles coordinating all the other components, and keeps track of in-progress games.

## Links

The server communicates with the client via websockets to send and receive events. The specifics can be found in the backend repository, in the file `api.md`.

The server communicates with the engine via POSIX pipes. The specifics can be found in the backend repository, in the file `engine.md`.

The server communicates with the database via SQL. See `db.md` in the backend repository for schema and connection details.
