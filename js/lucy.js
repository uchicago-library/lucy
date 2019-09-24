$(document).ready(function() {
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

  // Playable sound clips, e.g. in basic sentences sections.
  $('.playable').each(function() {
    var el = $(this);
    var url = $(this).attr('href').replace('http://', 'https://');
    $.ajax({
      dataType: 'text',
      success: function(data) {
        try {
          var arr = data.match(/iri="([^"]*)"/);
          el.attr('href', arr[1]);
        } catch (err) {
          console.log('Unable to locate audio file for the following element:');
          console.log(el);
        }
      },
      url: url,
    });
  });

  $('.playable').click(function(e) {
    e.preventDefault();
    var el = $(this);
    if (typeof el.data('sound') === 'undefined') {
      el.data('sound', new Howl({
        onend: function() {
          el.removeClass('paused playing');
          el.removeData('id sound');
          el.find('.slider').css('width', '0%');
        },
        src: [$(this).attr('href')]
      }));
    }
    if (!el.hasClass('playing')) {
      el.removeClass('paused').addClass('playing');
      if (typeof el.data('id') === 'undefined') {
          /* play from beginning */
          el.data('id', el.data('sound').play());
      } else {
          /* unpause */
          el.data('sound').play(el.data('id'));
      }
    } else {
      /* pause */
      el.removeClass('playing').addClass('paused');
      el.data('sound').pause(el.data('id'));
    }
  });

  // add a slider and slider track to all playable links.
  $('.playable').each(function() {
    $(this).append('<span class="slider_track"><span class="slider"/></span>');
  });

  // a function to update the slider position on playable things.
  function update_slider_positions() {
    $('.playing').each(function() {
      var width = $(this).data('sound').seek() / $(this).data('sound').duration() * 100;
      $(this).find('.slider').css(
        'width', 
        width + '%'
      );
    });
  }
  setInterval(update_slider_positions, 50);

  // basic sentences: toggle all breakdowns.
  $('#toggle_all_breakdowns').click(function(e) {
    e.preventDefault();
    $('.breakdown').toggle();
  });

  // basic sentences: toggle all transcriptions.
  $('#toggle_all_transcriptions').click(function(e) {
    e.preventDefault();
    $('.alternate_transcription').toggle();
  });

  // basic sentences: hide all translations.
  $('#hide_all_translations').click(function(e) {
    e.preventDefault();
    $('.translation').css('visibility', 'hidden');
  });

  // basic sentences: show all translations.
  $('#show_all_translations').click(function(e) {
    e.preventDefault();
    $('.translation').css('visibility', 'visible');
  });

  // basic sentences: hide all transcriptions.
  $('#hide_all_transcriptions').click(function(e) {
    e.preventDefault();
    $('.transcription').css('visibility', 'hidden');
  });

  // basic sentences: show all transcriptions.
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

  // basic sentences: next to the up arrow is a down arrow- this toggles alternate
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

  // vocabulary: contains column headers labelled "maya" and "english"
  // for sorting.
  $('.sort_vocabulary').click(function(e) {
    e.preventDefault();

    // figure out which column was clicked: Maya or English. 
    var column = $(this).text();
    $(this).closest('.vocabulary').data('column', column);

    // figure out if the sort should be ascending or descending. 
    var sort = '';
    if ($(this).closest('.vocabulary').data('sort') == undefined) {
      sort = 'descending';
    } else if ($(this).closest('.vocabulary').data('sort') == 'descending') {
      sort = 'ascending';
    } else {
      sort = 'descending';
    }
    $(this).closest('.vocabulary').data('sort', sort);

    // the first two divs should always be in the same place.
    // collect all the other divs into a list of two-tuples.
    var divs = [];
    for (var i = $('div.vocabulary > div.vocabulary_transcription').length-1; i >= 0; i--) {
      divs.push([
        $('div.vocabulary > div.vocabulary_transcription').eq(i).detach(),
        $('div.vocabulary > div.vocabulary_translation').eq(i).detach()
      ]);
    }

    // sort that list: ascending or descending based on the column. 
    divs.sort(function(a, b) {
      if (column == 'Maya') {
        var i = 0;
      } else {
        var i = 1;
      }
      if (a[i].text().toLowerCase() < b[i].text().toLowerCase()) {
        return -1;
      } else if (a[i].text().toLowerCase() > b[i].text().toLowerCase()) {
        return 1;
      } else {
        return 0;
      }
    })
    if (sort == 'descending') {
      divs.reverse();
    }

    // re-append the elements. 
    for (var i=0; i < divs.length; i++) {
      $('div.vocabulary').append(divs[i][0]);
      $('div.vocabulary').append(divs[i][1]);
    }
  });

  // conversation, situation narrative and conversation stimulus (see
  // lessons 6, 12, and 18) have "show", "show all", and "hide all"
  // buttons.

  // onload, hide these elements.
  $('table.conversation_stimulus td.response, table.question_and_answer td.response, table.situation_narrative td.transcription').css('visibility', 'hidden');

  // when the user clicks a "show" link, show (or hide) the appropriate
  // content.
  $('a.conversation_stimulus_show, a.question_and_answer_show, a.situation_narrative_show').click(function(e) {
    e.preventDefault();
    var td = $(this).closest('tr').find('td').last();
    if (td.css('visibility') == 'hidden') {
      td.css('visibility', 'visible');
      $(this).text('hide');
    } else {
      td.css('visibility', 'hidden');
      $(this).text('show');
    }
  });

  // when the user clicks "show all", show everything. 
  $('a.conversation_stimulus_show_all, a.question_and_answer_show_all, a.situation_narrative_show_all').click(function(e) {
    e.preventDefault();
    $(this).closest('table').find('tbody').find('tr').each(function() {
      $(this).find('td').last().css('visibility', 'visible');
      $(this).find('a.conversation_stimulus_show, a.question_and_answer_show, a.situation_narrative_show').text('hide');
    });
  });

  // when the user clicks "hide all", show everything. 
  $('a.conversation_stimulus_hide_all, a.question_and_answer_hide_all, a.situation_narrative_hide_all').click(function(e) {
    e.preventDefault();
    $(this).closest('table').find('tbody').find('tr').each(function() {
      $(this).find('td').last().css('visibility', 'hidden');
      $(this).find('a.conversation_stimulus_show, a.question_and_answer_show, a.situation_narrative_show').text('show');
    });
  });

  // The sidebar is set up to display all sub-lessons to visitors who
  // have JavaScript turned off. This removes the "flash of unstyled
  // content."
  $('body').removeClass('un_fouc');

  // the right arrow doesn't render correctly in Edge. Change it to the
  // greater than symbol in Edge or IE.
  if (navigator.appName == 'Microsoft Internet Explorer') {
    $('#sidebar span').text('>');
  }
});
