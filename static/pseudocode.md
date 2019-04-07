TO PUSH SKINCARE PRODUCTS TO AN ARRAY AND SORT BY MOST SIMILAR

set productId
set selectedProductArray
set mostSimilarIngredients equal to zero
declare mostSimilarIngredientsId
let similarProductsArray = []

for (n = 0; n < allProducts in API; n++)
    let productObject = allProducts[n]

    if (productObject.id != productId) {
        let similarIngredients = 0;
        for (i = 0; i < productArray.length; i++) {
            for(j = 0; j < productObject.ingredient_list.length; j++){
                if (productArray[i] === productObject.ingredient_list[j]){
                    similarIngredients++;
                }
            }
        }
        productObject = {
            brand: productObject.brand,
            id: productObject.id,
            ingredient_list: productObject.ingredient_list,
            name: productObject.name,
            similar_ingredients: similarIngredients
        }
        if similarProductsArray.length < 5
            push productObject to similarProductsArray
            sort similarProductsArray by similarProductsArray[i].similar_ingredients
        else if similarProductsArray.length > 5
            if productObject.similar_ingredient > similarProductsArray[4].similar_ingredients
                pop similarProductsArray[4]
                push productObject to similarProductsArray
                sort similarProductsArray by similarProductsArray[i].similar_ingredients
            }
    }

