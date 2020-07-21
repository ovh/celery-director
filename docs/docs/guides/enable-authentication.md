# Enable authentication

Director provide basic authentication. To enable it, you have to create users and set `DIRECTOR_AUTH_ENABLED` variable to **true** in the `.env` file.

## Manage user

You can manage users using the CLI.

```bash
$ director user [create|list|update|delete]
```

Create user example:

```bash
$ director user create john
```