
## Json Schema

### Input

```json
{
	"payload" : {
		"sender" : "str",
		"timestamp" : "str",
		"chain_id" : 0,
		"category" : "user" or "confirmation" or "command",
		"message" : "str"
	}
}
```

### Output

```json
{
	"payload" : {
		"sender" : "str",
		"timestamp" : "str",
		"chain_id" : 0,
		"category" : "normal" or "confirmation" or "error" or "command",
		"message" : "str",
		"final" : true or false
	}
}
```
