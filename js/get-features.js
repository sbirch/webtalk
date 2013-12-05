var SHORT_WORD_LEN = 3

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
    a_word_list.forEach(function(word) { 
        if (word.length > SHORT_WORD_LEN) {
            result.push(word);
        }
    });

    return result;
}

// returns the minimum edit distance between any word in word_set1 and any word in word_set
function minEditDistanceForWords(word_set1, word_set2) {
	var minDist = Infinity;
	word_set1.forEach(function(word1) {
		var d = minEditDistanceForWord(word1, word_set2);
		if (d < minDist) {
            minDist = d;
		}
    });

	return minDist;
}

// returns the minimum edit distance between word and any word in word_set
function minEditDistanceForWord(word, word_set) {
    // i think this could be optimized with BK trees or somesuch
	var minDist = Infinity;
	word_set.forEach(function(word2) {
		var d = getEditDistance(word, word2);
		if (d < minDist) {
            minDist = d;
		}
    });
	return minDist;
}

var Features = {
  // Returns true if the given element is visible or else false
  // Adapted from https://www.altamiracorp.com/blog/employee-posts/selenium-mojo-a-faster-isvisib
  // TODO: match behavior of this code with W3C spec (or else make approximations clear)
  // http://www.w3.org/TR/webdriver/#determining-visibility
  isVisible: function(element) {
    var visible = true;
    // Check if this is a hidden input element
    if (element.type && element.type == "hidden") {
      return false;
    }

    // if 0 x 0 return false
    if (element.clientWidth === 0 || element.clientHeight === 0){
      return false;
    }

    // Check this element and all parents for hidden style
    while (element != null) {
      var style = window.getComputedStyle(element);
      if (style && (style['display'] == 'none' || style['visibility'] == 'hidden')) {
        return false;
      }
      element = element.parentNode;
    }

    return visible;
  },

  // return a list of filtered words from the text of an element
  getTextWords: function(elem) {
	var words = []
	if (elem.value && this.isClickable(elem)) words.push(elem.value);
	if (elem.alt) words.push(elem.alt);
    return filter_word_list(elem.textContent.split(/\s+/).concat(words));
  },

  // produces a list of filtered words in text 
  // in sibling tags
  getSiblingTextWords: function(element) {
	  if (element.parentNode) {
		  return Features.getTextWords(element.parentNode);
	  } else {
		  return ["farts"];
	  }
  },

  isTypable: function(elem){
    if (elem.tagName == 'TEXTAREA'){return true;}
    else if (elem.tagName == 'INPUT' && _.contains(['text', 'email', 'password', 'search', 'url'], elem.type.toLowerCase())){
      return true;
    }
    return false;
  },

  isClickable: function(elem){
    if (elem.tagName == 'BUTTON' || elem.tagName == 'A'){return true;}
    else if (elem.tagName == 'INPUT' && _.contains(['submit', 'button', 'checkbox', 'radio'], elem.type.toLowerCase())){
      return true;
    }
    return false;
  }
}

function elementToFeatureVector(elem) {
    var rect = elem.getBoundingClientRect();

    // FIX:
      // best relative_x is 0
      // edit distances are all best at 0
      // text size & n_children?

    return {
      width: rect.width,
      height: rect.height,


      // Note! relative_x and relative_y are both further modified in extend_and_norm_feature.

      // 0 = center of the page
      relative_x: Math.abs((rect.left + window.scrollX - document.body.clientWidth*0.5) / document.body.clientWidth),
      // higher = further down
      // 0 = top of page, 1 = at fold
      relative_y: ((rect.top +  window.scrollY) / window.innerHeight),

      clickable: Features.isClickable(elem)? 1:-1,
      typeable: Features.isTypable(elem)? 1:-1,

      tagname: elem.tagName,
      text_words: Features.getTextWords(elem),
      sibling_text_words: Features.getSiblingTextWords(elem),

      text_size: Features.getTextWords(elem).length,
      n_children: elem.children.length,
      tab_index: (elem.tabIndex == -1)? -1:1,

      id: elem.id,
      class_list: elem.classList,
      has_id: (elem.id === '')? 0:1,
      has_class: (elem.classList.length > 0)? 1:0,

      alreadyInteracted: elem.getAttribute("x-WebtalkInteracted") == "1"? -1:1,
    }
}

// produces a list of all Elements in the body of the page that are currently visible
function getAllElementFeatures(){
  function recGetAllElems(root) {
    var elements = [];
    for(var i=0;i<root.children.length;i++){
            var this_child = root.children[i];
            if (!Features.isVisible(this_child) || this_child.id.substring(0,18) == 'selenium-highlight'){
              continue;
            }
            elements.push([this_child, elementToFeatureVector(this_child)])
            elements = elements.concat(recGetAllElems(this_child));
    }
    return elements
  }

  return recGetAllElems(document.body);
}

function elementTree(){
  function rec(root) {
    var elements = [];
    for(var i=0;i<root.children.length;i++){
            var this_child = root.children[i];

            if (!Features.isVisible(this_child)){
              continue;
            }

            var label = this_child.tagName + (this_child.id? '#'+this_child.id:'');

            elements.push([label, rec(this_child)]);
    }
    return elements;
  }

  return ['BODY', rec(document.body)];
}

res = getAllElementFeatures()

return [
  res,
  elementTree(document.body)
]
