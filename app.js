// REQUIRES
var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var multer = require('multer');
var fs = require('fs');
var mysql = require("mysql");
var PythonShell = require('python-shell');
var private = require('./private.js');


// CONNECT TO DB
var con = private.connectDB();

con.connect(function(err){
  if(err){
    console.log('Error connecting to Db');
    return;
  }
  console.log('Connection established');
});

// SET UP THE UPLOAD PROC
var uploaded = [];
var storage = multer.diskStorage({
  destination: function (req, file, callback) {
    callback(null, './public/images');
  },
  filename: function (req, file, callback) {
    var name = file.fieldname + '-' + Date.now() + file.mimetype.replace('image/','.');
    uploaded.push('/public/images/'+name);
    callback(null, name);
  }
});
var upload = multer({ storage : storage}).single('file');


// RUN EXPRESS
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());

// DEFINE ROUTES
app.post('/file-upload', function (req, res) {
    upload(req,res,function(err) {
        if(err) {
            return res.end("Error uploading file.");
        }
        res.end("File is uploaded");
    });
});

app.post('/process', function (req, res) {
    if(uploaded.length == 0)
        return;
    
    var results = [];
    var similarImages = [];
    
    // FOR DEBUG
    var m;
    var pyshell = new PythonShell('testing.py');
    pyshell.send('4');
    pyshell.on('message', function (message) {
      console.log(message);
        m=message;
    });
    pyshell.end(function (err) {
      if (err) throw err;
      console.log('finished');
    });
    res.json({result:[{disease: 'Something', index:0}]});
    return;
    
    for(var i = 0; i<uploaded.length; i++) {
        
        // run image analysis TODO
        var pyshell = new PythonShell('testing.py');
        pyshell.send('hello');
        pyshell.on('message', function (message) {
          console.log(message);
        });
        pyshell.end(function (err) {
          if (err) throw err;
          console.log('finished');
        });

        // object returned by analysis
        var result = {
            name : 'name',
            totalStainedCells : 0,
            disease : 'disease',
            x : 0,
            y : 0,
            z : 0
        };
        
        results.push(result);

        // get similar images
        var similar = [];
        var query = `SELECT name, ABS(total_stained_cells - ?) as diff FROM blood_db.main
                    ORDER BY diff 
                    LIMIT 5`;
        con.query(query, [result.totalStainedCells], function(err,rows){
            if(err) throw err;

            console.log('Data received from Db:\n');
            console.log(rows);
            similar.push(rows);
        });
        
        similarImages.push(similar);
        
    }

    // update the table with new data
    var query = '';
    var params = [];
    for(var i = 0; i<results.lenght; i++) {
        var r = results[i];
        query += `INSERT INTO blood_db.main (name, total_stained_cells, disease_tag)
                  VALUES (?, ?, ?);
                  INSERT INTO blood_db.stained_cells_position (fk_main_id, x, y, z)
                  SELECT id, ?, ?, ? FROM blood_db.main where name=?;`;
        params = params.concat([r.name, r.totalStainedCells, r.disease, r.x, r.y, r.z, r.name]);
    }
    
    // run insert query
    con.query(query, params, function (err, result) {
        if(err) throw err;
        console.log("Inserted" + result);
    });
    
    res.end({
        results : results,
        similar : similarImages
    });
});

app.post('/feedback', function (req, res) {
    // update the user feedback in the db
    
    var stars = req.body.stars;
    console.log('body: ' + stars);
    
    con.query('UPDATE main SET feedback = ? WHERE name = ?;', 
        [stars, uploaded[0]],
        function (err, result) {
        if (err) throw err;

        console.log('Changed ' + result.changedRows + ' rows');
        }
    );
    
});


// LISTEN TO PORT
app.listen(3000);


// TERMINATE DB CONNECTION
con.end(function(err) {
  // The connection is terminated gracefully
  // Ensures all previously enqueued queries are still
  // before sending a COM_QUIT packet to the MySQL server.
});