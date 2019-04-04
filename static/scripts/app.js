// $('.test-search-btn').click(function(e) {
//     console.log("You clicked the search button!")
//     $('.search-results').empty();
//     let inputVal = $('.product-input').val();
//     console.log(inputVal)
//     let formattedInput = inputVal.replace(/ /g, '+');
//     let searchTerm = "drunk+elephant"
//     $.ajax({
//         method: 'GET',
//         url: `https://skincare-api.herokuapp.com/product?q=${formattedInput}&limit=25&page=1`,
//         success: function (response) {
//             console.log(response)
//             response.map(child => {
//                 let productId = child.id;
//                 let productLink = `<a href="http://localhost:8000/product/${productId}">${child.brand} ${child.name}</a>`;
//                 let card = $(`<div class="card search-wrapper"/>`);
//                 let btn = $(
//                   `<input class="now-playing-button btn btn-dark btn-block" type=submit value="View Product" data-id="${productId}"></input>`
//                 );
//                 let url = 'https://image.tmdb.org/t/p/w500' + child.poster_path;
//                 card.append(productLink)
//                 $('.search-results').append(card);
//                 return productId;
//               });


//         },
//         error: function(error) {
//             console.log(error);
//         }
//     })
// })