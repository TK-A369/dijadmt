# DIJADMT User Guide

DIJADMT is configured using TOML files. Those are intended to be held in a Git repository, although it is not a requirement.

For TOML syntax details, refer to (https://toml.io/en/).

DIJADMT is invoked as: `dijadmt <root_conf> [options]`. For details, run `dijadmt -h`.

The `<root_conf>` is the path to the root configuration file.

## TOML config files

Every TOML configuration file may contain the following keys: `enable`, `subconfs`, `defs` and `groups`.

`enable` should be an array of groups that should be enabled. Currently, it is only recognized on the top-level config file.

`subconfs` should be an array of names of the TOML files to import.

`defs` should be a table. For every key-value pair, a variable will be created, with name being the key, and the value being the value.

`groups` should be a table. Every key-value pair in it defines a group, with name being the key. The value should be a table with the following keys: `in_path`, `out_path`, `process` (optional), `requires` (optional; a list of dependencies) and `conflicts` (optional; a list of conflicting groups).

## File processors

### `none`

Simply symlink input files to destination.

### `defsubs`

The following substitutions will be performed:

- `$dijadmt_def{var}` - expands to the value of given variable; will raise an error if the variable is undefined
- `$dijadmt_if{var}{value}{content}` - if given variable is equal to given variable, then expand to the content; otherwise expand to empty string
- `$dijadmt_escape{c}` - expand to given single character
