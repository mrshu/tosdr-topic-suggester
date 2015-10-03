var dir = require('node-dir');
var jf = require('jsonfile');
var fs = require("fs");

String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

dir.files('./tosdr.org/points/', function (err, files) {
  if (err) throw err;
  var out = [];
  (function next(){
    var path = files.pop();

    if (!files.length) {
      fs.writeFile('tosdr-dataset.json', JSON.stringify(out), function (err) {
        if (err) throw err;

        console.log('Dataset prepared.');
      });
      return;
    }

    if (!path.endsWith('.json')) {
      next();
      return;
    }

    jf.readFile(path, function (err, obj) {
      if (err) throw err;

      if (obj.topics !== undefined) {
        var topic = obj.topics.pop();
        var title = obj.title ? obj.title : '';
        var description = obj.tosdr.tldr ? obj.tosdr.tldr : '';
        out.push({
          'topic': topic,
          'title': title,
          'description': description
        });
      }

      next();
    });
  })();
});
