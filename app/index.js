const elasticsearch = require('elasticsearch');
const client = new elasticsearch.Client({
   hosts: [ 'http://localhost:9200']
});
const express = require( 'express' );
const app = express();
const bparser = require('body-parser')
const path = require( 'path' );

client.ping({
     requestTimeout: 30000,
 }, function(error) {
     if (error) {
         console.error('elasticsearch cluster is down!');
     } else {
         console.log('Everything is ok');
     }
 });


app.use(bparser.json())

// set port for the app to listen on
app.set( 'port', process.env.PORT || 3001 );
app.use( express.static( path.join( __dirname, 'public' )));
// enable CORS
app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS');
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.get('/', function(req, res){
  res.sendFile('template.html', {
     root: path.join( __dirname, 'views' )
   });
})

app.get('/search', function (req, res){
  console.log(req.query['q']);
  console.log(req.params)
  // //readQuery(req.query['q']).catch(console.log).then(data => {
  // //  res.send(results.hits.hits);
  // })

  let body = {
    query: {
        match: { 
          "url_title": req.query["q"]
          //"_id": "8DUe-HkBphMV6ELg4M2I"
        }
    }
  }
  client.search({index:'url',  body: body, type:'url_info'})
  .then(results => {
    console.log('here');
    console.log(results.hits);
    res.send(results.hits.hits);
  })
  .catch(err=>{
    console.log('In error');
    console.log(err);
    res.send([]);
  });
})

app .listen( app.get( 'port' ), function(){
  console.log( 'Listening on port ' + app.get( 'port' ));
} );