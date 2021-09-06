
var json_path = process.argv.slice(2)
console.log(json_path)
var inputfile =  require("../" + json_path + "/crawl_results.json");
var bulk = [];
const es = require('elasticsearch')
const client = new es.Client({
    host: 'http://localhost:9200',
})

client.ping({
    requestTimeout: 30000,
}, function(error) {
    if (error) {
        console.error('Elasticsearch cluster is down!');
    } else {
        console.log('Everything is ok');
    }
});

client.indices.create({  
    index: 'url',
    type: 'url_info'
  },function(err,resp,status) {
    if(err) {
      console.log(err);
    }
    else {
      console.log("create",resp);
    }
  });

var makebulk = function(url_list,callback){
  for (var current in url_list){
    bulk.push(
      { index: {_index: 'url', _type: 'url_info' } },
      {
        'url_title': url_list[current].title,
        'url_link': url_list[current].page_url,
        'contents': url_list[current].body
      }
    );
  }
  callback(bulk);
}

var indexall = function(madebulk,callback) {
  client.bulk({
    maxRetries: 5,
    index: 'url',
    type: 'url_info',
    body: madebulk
  },function(err,resp,status) {
      if (err) {
        console.log(err);
      }
      else {
        callback(resp.items);
      }
  })
}

makebulk(inputfile,function(response){
    console.log("Bulk content prepared");
    indexall(response,function(response){
        console.log(response);
})
});