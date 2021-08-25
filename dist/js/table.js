$(document).ready( function () {
  
    var table = $('#example').DataTable({
            lengthMenu: [ [20, 50, 100, -1], [20, 50, 100, "All"] ],
            pageLength: 50,
            orderCellsTop: true,
            fixedHeader: true,
            "ajax": "../data/data.json",
                "columns": [
                    { "data": "id" },
                    { "data": "topic" },
                    { "data": "subtopic" },
                    { "data": "type" },
                    { "data": "name" },
                    { "data": "status" },
                    { "data": "date_started" },
                    { "data": "date_published" },
                    { "data": "date_reviewed" },
                    { "data": "maturity" },
                    { "data": "legal" },
                    { "data": "version" }
                  ],
              initComplete: function () {
              count = 0;
              this.api().columns().every( function () {
                  var title = this.header();
                  //replace spaces with dashes
                  title = $(title).html().replace(/[\W]/g, '-');
                  var column = this;
                  var select = $('<select id="' + title + '" class="select2" ></select>')
                      .appendTo( $(column.footer()).empty() )
                      .on( 'change', function () {
                        //Get the "text" property from each selected data 
                        //regex escape the value and store in array
                        var data = $.map( $(this).select2('data'), function( value, key ) {
                          return value.text ? '^' + $.fn.dataTable.util.escapeRegex(value.text) + '$' : null;
                                   });
                        
                        //if no data selected use ""
                        if (data.length === 0) {
                          data = [""];
                        }
                        
                        //join array into string with regex or (|)
                        var val = data.join('|');
                        
                        //search for the option(s) selected
                        column
                              .search( val ? val : '', true, false )
                              .draw();
                      } );
   
                  column.data().unique().sort().each( function ( d, j ) {
                      select.append( '<option value="'+d+'">'+d+'</option>' );
                  } );
                
                //use column title as selector and placeholder
                $('#' + title).select2({
                  multiple: true,
                  closeOnSelect: false,
                  placeholder: "Select a " + title
                });
                
                //initially clear select otherwise first option is selected
                $('.select2').val(null).trigger('change');
              } );
          }
    });
  } );
