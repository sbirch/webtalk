var SHORT_WORD_LEN = 3
var word_list = filter_word_list(arguments[0])
// Compute the edit distance between the two given strings
// Taken from: http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#JavaScript
function getEditDistance(a, b){
  if(a.length == 0) return b.length; 
  if(b.length == 0) return a.length; 
 
  var matrix = [];
 
  // increment along the first column of each row
  var i;
  for(i = 0; i <= b.length; i++){
    matrix[i] = [i];
  }
 
  // increment each column in the first row
  var j;
  for(j = 0; j <= a.length; j++){
    matrix[0][j] = j;
  }
 
  // Fill in the rest of the matrix
  for(i = 1; i <= b.length; i++){
    for(j = 1; j <= a.length; j++){
      if(b.charAt(i-1) == a.charAt(j-1)){
        matrix[i][j] = matrix[i-1][j-1];
      } else {
        matrix[i][j] = Math.min(matrix[i-1][j-1] + 1, // substitution
                                Math.min(matrix[i][j-1] + 1, // insertion
                                         matrix[i-1][j] + 1)); // deletion
      }
    }
  }
 
  return matrix[b.length][a.length];
};


function filter_word_list(a_word_list) {
    var result = []
    for (word in a_word_list) { 
        if (word.length > SHORT_WORD_LEN) {
            result.push(word);
        }
    }

    return result;
}

function minEditDistanceForWords(word_set1, word_set2) {
}

// returns the minimum edit distance between word and any word in word_set
function minEditDistanceForWord(word, word_set) {
    // i think this could be optimized with BK trees or somesuch
	var minDist = Infinity;
	for (word2 in word_set) {
		d = getEditDistance(word, word2);
		if (d < minDist) {
			d = minDist;
		}
	}

	return minDist;
}



var Features = {
  // Returns true if the given element is visible or else false
  // Taken from: ????!!?!?
  // TODO: match behavior of this code with W3C spec (or else make approximations clear)
  // http://www.w3.org/TR/webdriver/#determining-visibility
  isVisible: function(element) {
    var visible = true;
    // Check if this is a hidden input element
    if (element.type && element.type == "hidden") {
      return false;
    }

    // Check this element and all parents for hidden style
    while (element != null) {
      if (element.currentStyle && (element.currentStyle['display'] == 'none' || element.currentStyle['visibility'] == 'hidden')) {
        visible = false;
        break;
      }
      element = element.parentNode;
    }

    return visible;
  }

}

function elementToFeatureVector(elem) {
    // Features TODO:
      // text matching of element & relatives
      // position (relative to last action?)
      // scrolled into view?
      // color?
      // CSS class names
      // tabIndex

    // Features in python_style since it's being shipped off there
    return [Features.isVisible(elem)? 1:0]
}

// produces a list of all Elements in the body of the page that are currently visible
function getAllElementFeatures(){
  function recGetAllElems(root) {
    var elements = [];
    for(var i=0;i<root.children.length;i++){
            elements.push(elementToFeatureVector(root.children[i]))
            elements = elements.concat(recGetAllElems(root.children[i]));
    }
    return elements;
  }

  return recGetAllElems(document.body);
}

feats = getAllElementFeatures()
return feats