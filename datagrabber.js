#!/usr/bin/env node

var dir = require('node-dir');
var jf = require('jsonfile');
var fs = require("fs");

String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

dir.files('./tosdr.org/topics/', function (err, files) {
  if (err) throw err;
  var topics = [];
  (function next(){
    var path = files.pop();

    if (!files.length) {
      dump(topics);
      return;
    }

    if (!path.endsWith('.json')) {
      next();
      return;
    }

    path = path.replace(/.*\/([^\.]+)\.json/, "$1");
    topics.push(path);

    next();
  })();
});

function dump(topics) {
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

          topic = topic.replace('user information', 'user-info');
          topic = topic.replace('personal information', 'personal-data');
          topic = topic.replace(' ', '-')
          topic = topic.replace(/^scope.*license$/, 'copyright-scope');
          topic = topic.replace(/^law.*gov.*/, 'law-gov');
          topic = topic.replace(/^third.*/, 'third');
          topic = topic.replace(/\%.*$/, '');

          if (topics.indexOf(topic) == -1) {
            next();
            return;
          }

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
}
