# Known issues
* sql injection

## In progress
* sql injection

db execution in *query_db* changed to:
```
db.execute(query, parameters)
```

Example query:
```
query_db('SELECT * FROM Users WHERE username=?;',parameters=[form.login.username.data], one=True)
```
Database stuff should probably be moved to a separate class.

## Fixed