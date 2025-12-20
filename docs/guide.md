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

### `ngproc`

The New Generation Processor is more advanced successor to `defsubs`. While `defsubs` simply used regular expressions to find expressions to evaluate, `ngproc` has a dedicated parser that constructs an AST which is then evaluated.

The syntax was initially intended to be an extension on the one of `defsubs`, but now it isn't compatible with it. The entire document is a series of expressions. An expression can a dollar expression, an escape sequence, a normal character or a brace enclosed expression.

A dollar expression begins with a dollar sign `$` followed by a function name (that must begin with `dijadmt_` - it is enforced at the parser level) and any number of arguments. Each argument is enclosed in double braces (`{{` and `}}`), and its content is any number of expressions.

An escape sequence can be one of the following: `\{` (gives `{`), `\}` (gives `}`) and `\$` (gives `$`).

A normal character can be anything besides braces (`{` and `}`).

A brace enclosed expression is enclosed by single braces (`{` and `}`) and its content is any number of expressions. The braces must be properly paired.

Escape sequences evaluate to the corresponding character. Normal characters evaluate to themselves. Brace enclosed expressions retain the braces and evaluate the content.

There are the following dollar expression functions:

- `$dijadmt_def{{var}}` - returns the value of given variable
- `$dijadmt_if{{var}}{{value}}{{content}} - reads given variable and if it is equal to value, then return content; otherwise return empty string

It is important to note that the parser uses backtracking - if one matching one rule failed when a few alternatives are possible, others will be tried, according to their order. Also, the normal char may be a dollar sign. The consequence of those two is that you are allowed to use dollar sign in your configuration files and if it doesn't match the dollar expression syntax rules, it will be passed literally - so you can use Bourne shell-style variables without escaping the dollar sign. You can also write JSON without much trouble, by using brace enclosed expressions.
