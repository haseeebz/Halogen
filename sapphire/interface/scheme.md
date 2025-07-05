
## Json Schema

### Input

#### For Commands

```json
{
	"type" : "command",
	"payload" : {
		"sender" : "str",
		"timestamp" : "str",
		"chain_id" : 0,
		"cmd" : "str",
		"args": ["str"]
	}
}
```

#### For User Input

```json
{
	"type" : "user",
	"payload" : {
		"sender" : "str",
		"timestamp" : "str",
		"chain_id" : 0,
		"category" : "user" or "confirmation",
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
