# API calls

This file includes all API calls to the backend and their responses. Variable values are indicated with `<type of value>`.

Every message should have an "id" field. It should be a unique integer. All messages should be acknowledged with a message of the following format with a matching "id":

```
{
  "type":"ack",
  "id":<int>,
  "code":<int>,
}
```

The meaning of the code field is enumerated here:

| Code | Meaning                                        |
|-----:|:-----------------------------------------------|
|   -1 | Internal server error.                         |
|    0 | All good.                                      |
|    1 | Miscellaneous error.                           |
|    2 | Bad message (formatting, missing field, etc.). |
|    3 | Not logged in.                                 |
|    4 | Invalid username or password.                  |
|    5 | Username taken or malformed.                   |
|    6 | Password taken or malformed.                   |
|    7 | Invalid move.                                  |
|    8 | Not your turn.                                 |

Some message will have additional return values in this message (like returning a game code upon game creation).

# Client Messages

## signup

Sign up and make a new account.

```
{
  "type":"signup",
  "id":<int>,
  "name":<string>,
  "pass":<string>,
}
```

## login

Log in to an existing account.

```
{
  "type":"login",
  "id":<int>,
  "name":<string>,
  "pass":<string>,
}
```

## game_request

Request to enter the public game pool.

```
{
  "type":"game_request",
  "id":<int>,
}
```

## game_create

Create a private game.

```
{
  "type":"game_create",
  "id":<int>,
  /* Put some options here eventually */
}
```

Additional return fields:

```
{
  ...,
  "code":<int>, /* Game code, to be used in "game_join". */
}
```

## game_join

Join a private game.

```
{
  "type:"game_join",
  "id":<int>,
  "code":<string>,
}
```

## game_modify

Modify an existing game, mostly for settings like player count.

```
{
  "type:"game_modify",
  "id":<int>,
  /* Put some settings here */
}
```

## move

Make a move.

```
{
  "type:"move",
  "id":<int>,
  /* However we want to represent moves. */
}
```

# Server Messages

## game_state

Inform a client of a change in game state.

```
{
  "type:"game_state",
  "id":<int>,
  "state": /* However we want to represent state. */
}
```
