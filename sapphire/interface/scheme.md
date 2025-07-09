
## Json Schema
Only for reference.
### Input

```json
{
	{
		"sender" : "client",
		"timestamp" : "22:12:19",
		"chain" : { "context" : 1, "flow" : 3 },
		"category" : "user" or "confirmation" or "command",
		"message" : ""
	}
}
```

### Output

```json
{
	{
		"sender" : "core",
		"timestamp" : "str",
		"chain" : { "context" : 1, "flow" : 3 },
		"category" : "normal" or "confirmation" or "error" or "command",
		"message" : "",
		"final" : false
	}
}
```
