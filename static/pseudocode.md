TO COMPARE SKINCARE PRODUCT ARRAYS

set selectedProductId
set selectedProductArray
set mostSimilarIngredients equal to zero
declare mostSimilarIngredientsId

declare similarIngredientsOne
declare similarIngredientsTwo

for (n = 0; n < allProducts in API; n+=2>)

    set firstArray to allProducts[n].ingredient_list
    set secondArray to allProducs[n+1].ingredient_list

    loop through selectedProductArray
        set firstArrayId to allProducts[n].id
        if firstArrayId !== selectedProductId
            loop through firstArray
                compare selectedProductArray[i] to firstArray[j]
                if equal, increment similarIngredientsOne variable

    loop through selectedProductArray
        set secondArrayId to allProducts[n].id
        if firstArrayId !== selectedProductId
            loop through secondArray
                compare selectedProductArray[i] to secondArray[j]
                if equal, increment similarIngredientsTwo variable

    if similarIngredientsOne is greater than similarIngredientsTwo AND greater than mostSimilarIngredients
        then set mostSimilarIngredients to similarIngredientsOne
        and set mostSimilarIngredientsId to firstArrayId

    else if similarIngredientsTwo is greater than similarIngredientsOne AND greater than mostSimilarIngredients
        then set mostSimilarIngredients to similarIngredientsTwo
        and set mostSimilarIngredientsId to secondArrayId

    else if similarIngredientsOne is equal to similarIngredientsTwo
        then set mostSimilarIngredients to similarIngredientsOne
        and set mostSimilarIngredientsId to firstArrayId
        and set anotherMostSimilarIngredientsId to secondArrayId