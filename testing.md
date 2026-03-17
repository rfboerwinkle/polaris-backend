This document is a draft that briefly outlines the testing that will occur across the entire project.

# Component Testing

Unit testing will be mainly used for testing individual components of our project, especially on backend (such as testing API functions)

# Integration Testing

Integration testing will be used to ensure proper behavior between backend and database. This method will also be used to test websocket/API response behavior between backend and frontend.

# Performance Testing

Since the application is aimed to have numerous concurrent users connected and playing, some performance testing on the websocket and other resources that digitally within our control will be done to ensure smooth and timely responses to users

# Testing via Simulation

Once the core requirements are met and the application is functional, testing the full process will occur to ensure no major bugs are falling though the previous testing methods. This will include our required functionalities such as account creation, match creating/joining, playing though a game at different amounts of players, etc.