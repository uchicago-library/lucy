$(document).ready(function() {
  // the right arrow doesn't render correctly in Edge. Change it to the
  // greater than symbol in Edge or IE.
  if (navigator.appName == 'Microsoft Internet Explorer') {
    $('#sidebar span').text('>');
  }

  // Set up the mouseover and mouseout events to reveal or hide
  // sub-lessons in the sidebar navigation.
  $('#sidebar li').mouseover(function() {
    $('#sidebar li ul').css('display', 'none');
    $(this).find('ul').css('display', 'block');
  });
  $('#sidebar').mouseout(function() {
    $('#sidebar li ul').css('display', 'none');
  });
  $('#sidebar').css('display', 'block');

  // toggle all breakdowns.
  $('#toggle_all_breakdowns').click(function(e) {
    e.preventDefault();
    $('.breakdown').toggle();
  });

  // toggle all transcriptions.
  $('#toggle_all_transcriptions').click(function(e) {
    e.preventDefault();
    $('.alternate_transcription').toggle();
  });

  // hide all translations.
  $('#hide_all_translations').click(function(e) {
    e.preventDefault();
    $('.translation').css('visibility', 'hidden');
  });

  // show all translations.
  $('#show_all_translations').click(function(e) {
    e.preventDefault();
    $('.translation').css('visibility', 'visible');
  });

  // hide all transcriptions.
  $('#hide_all_transcriptions').click(function(e) {
    e.preventDefault();
    $('.transcription').css('visibility', 'hidden');
  });

  // show all transcriptions.
  $('#show_all_transcriptions').click(function(e) {
    e.preventDefault();
    $('.transcription').css('visibility', 'visible');
  });

  // on basic sentences sub-lessons, an up arrow appears to the right of
  // each translation / transcription pair. This toggles breakdowns of
  // each sentence. 
  function toggle_breakdowns(e) {
    var height_a = $('#basic_sentences').height();
    e.preventDefault();
    var el = $(this).parents('tr:first').prevAll('.breakdown:first');
    while (el.length && el.hasClass('breakdown')) {
      el.toggle();
      el = el.prev();
    }
    var height_b = $('#basic_sentences').height();
    if (height_b > height_a) {
      $('#basic_sentences').css('top', height_a - height_b);
    } else {
      $('#basic_sentences').css('top', 0);
    }
  }
  $('.toggle_breakdowns').click(toggle_breakdowns);

  // next to the up arrow is a down arrow- this toggles alternate
  // transcriptions of each sentence. 
  function toggle_alternate_transcriptions(e) {
    e.preventDefault();
    var el = $(this).parents('tr:first').nextAll('.alternate_transcription:first');
    while (el.length && el.hasClass('alternate_transcription')) {
      el.toggle();
      el = el.next();
    }
  }
  $('.toggle_alternate_transcriptions').click(toggle_alternate_transcriptions);

  // The sidebar is set up to display all sub-lessons to visitors who
  // have JavaScript turned off. This removes the "flash of unstyled
  // content."
  $('body').removeClass('un_fouc');

  /*
  var sound = new Howl({
    src: ['/audio/1.1.mp3']
  });
  sound.play();
  */
  /*
  $('.playable').each(function() {
    var href = $(this).attr('href').replace('http://', 'https://');
    console.log(href);
    $.get(href, function(data) {
      return;
      console.log(data);
      console.log(data.getElementsByTagName('identification')[1].attributes);
      // xmlns:ino="http://namespaces.softwareag.com/tamino/response2"
      // xmlns:xql="http://metalab.unc.edu/xql/"
      // xmlns:xq="http://namespaces.softwareag.com/tamino/XQuery/result"
      // /ino:response/xq:result/ochre/resource/identification/@iri
    });
  });
  */

  $.get('https://ochre.lib.uchicago.edu/ochre?uuid=93cc3a42-88c9-414f-b263-02c785ab479b', function(data) {
    console.log('!!!!!!!');
    console.log(data);
    console.log($(data).find('identification').attributes['iri'].value);
    console.log(data.getElementsByTagName('identification')[0].attributes['iri'].value);
    console.log(data.getElementsByTagName('identification')[1].attributes['iri'].value);
    console.log(data.getElementsByTagName('identification')[1].attributes.getNamedItem('iri'));
    // console.log(identifications[1].attributes.getNamedItem('iri'));
    // console.log(data.getElementsByTagName('identification'));
  });
});
