# Caterpillar
**Super-lightweight & extensible markup language parser, written in Python, created for school project**

### How to download?
`git clone https://github.com/Pugneum-H/Caterpillar.git`

### How to use?
1. **import**:
`import caterpillar`
2. **initialization**:
`caterpillar.Caterpillar(*plugins, **settings)` - *current settings are :*
	- `silenced` - *disable/enable logging*
	- `encoding` - *encoding for plugins*
	- `handlers` - *handlers for logging*
	- `*plugins` - any path/URL to the file | python code* & parameters
3. **plugins**:
	- To add: `addPlugins(self, *plugins)`
	- To remove : `removePlugins(self, *plugins)`
4. **settings**
	- To update `updateSettings(self, **settings_)`
5. **parsing**:
	`parseText(self, text_)`

### End for now.

*(P.S. school project passed!)*
