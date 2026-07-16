# Session title settings UI pattern

Use when working on Hermes Web UI settings for session title behavior.

## Preferred surface

Keep the main Session settings tab compact and behavior-oriented:

```txt
Session titles                     AI-generated      [ Configure ]
```

or, when deterministic naming is selected:

```txt
Session titles                     First message     [ Configure ]
```

Do not show implementation details on the main settings page, such as `title_generation`, auxiliary task names, provider routing, or model-call plumbing.

## Configure dialog

Put details behind `Configure`:

```txt
Session titles

Mode
○ First message
  Use the first words of the first user message.

● AI-generated
  Generate a short title after the first assistant reply.

Model
● Same as chat model
○ Custom model

Prompt
Default prompt                                      [ Edit ]

[ Reset to default ]                 [ Cancel ] [ Save ]
```

When `First message` is selected, hide model and prompt controls. When `AI-generated` + `Custom model` is selected, show provider/model selectors.

## Copy rule

Describe visible behavior, not architecture:

- Good: `First message`, `AI-generated`, `Same as chat model`, `Custom model`.
- Bad: `The title model is selected through the auxiliary task configuration for title_generation.`

## Rationale

Session titles are always created; the setting chooses the naming mode. Avoid binary `On/Off` language unless the product truly disables all title behavior.