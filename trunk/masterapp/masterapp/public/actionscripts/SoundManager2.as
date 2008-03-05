/*
   SoundManager 2: Javascript Sound for the Web
   --------------------------------------------
   http://www.schillmania.com/projects/soundmanager2/

   Copyright (c) 2007, Scott Schiller. All rights reserved.
   Code licensed under the BSD License:
   http://www.schillmania.com/projects/soundmanager2/license.txt

   V2.0b.20070415

   Compiling AS to Flash 8 SWF using MTASC (free compiler - http://www.mtasc.org/):
   mtasc -swf soundmanager2.swf -main -header 16:16:30 SoundManager2.as -version 8

   ActionScript Sound class reference (Macromedia):
   http://livedocs.macromedia.com/flash/8/main/wwhelp/wwhimpl/common/html/wwhelp.htm?context=LiveDocs_Parts&file=00002668.html
*/

import flash.external.ExternalInterface; // woo

class SoundManager2 {

  static var app : SoundManager2;

  function SoundManager2() {

  // externalInterface references (for Javascript callbacks)
  var baseJSController = "soundManager";
  var baseJSObject = baseJSController+".sounds";

  // internal objects
  var sounds = []; // indexed string array
  var soundObjects = []; // associative Sound() object array
  var timer = null;
  var timerInterval = 50;
  var pollingEnabled = false; // polling (timer) flag - disabled by default, enabled by JS->Flash call

  var writeDebug = function(s) {
    ExternalInterface.call(baseJSController+"['_writeDebug']","(Flash): "+s);
  }

  var _externalInterfaceTest = function() {
    writeDebug('_externalInterfaceTest()');
    return true; // to verify that a call from JS to here, works. (eg. JS receives "true", thus OK.)
  }

  var checkProgress = function() {
    var bL = 0;
    var bT = 0;
    var nD = 0;
    var nP = 0;
    var oSound = null;
    for (var i=0,j=sounds.length; i<j; i++) {
      oSound = soundObjects[sounds[i]];
      bL = oSound.getBytesLoaded();
      bT = oSound.getBytesTotal();
      nD = oSound.duration||0; // can sometimes be null with short MP3s? Wack.
      nP = oSound.position;
      if (bL && bT && bL != oSound.lastValues.bytes) {
        oSound.lastValues.bytes = bL;
        ExternalInterface.call(baseJSObject+"['"+oSound.sID+"']._whileloading",bL,bT,nD);
      }
      if (typeof nP != 'undefined' && nP != oSound.lastValues.position) {
        oSound.lastValues.position = nP;
        ExternalInterface.call(baseJSObject+"['"+oSound.sID+"']._whileplaying",nP);
        // if position changed, check for near-end
        if (oSound.didJustBeforeFinish != true && oSound.loaded == true && oSound.justBeforeFinishOffset > 0 && nD-nP <= oSound.justBeforeFinishOffset) {
          // fully-loaded, near end and haven't done this yet..
          ExternalInterface.call(baseJSObject+"['"+oSound.sID+"']._onjustbeforefinish",(nD-nP));
          oSound.didJustBeforeFinish = true;
        }
      }
    }
  }

  var onLoad = function(bSuccess) {
    checkProgress(); // ensure progress stats are up-to-date
    // force duration update (doesn't seem to be always accurate)
    ExternalInterface.call(baseJSObject+"['"+this.sID+"']._whileloading",this.getBytesLoaded(),this.getBytesTotal(),this.duration);
    ExternalInterface.call(baseJSObject+"['"+this.sID+"']._onload",bSuccess?1:0);
  }

  var onID3 = function() {
    // --- NOTE: BUGGY? ---
    // --------------------
    // TODO: Investigate holes in ID3 parsing - for some reason, Album will be populated with Date if empty and date is provided. (?)
    // ID3V1 seem to parse OK, but "holes" / blanks in ID3V2 data seem to get messed up (eg. missing album gets filled with date.)
    // iTunes issues: onID3 was not called with a test MP3 encoded with iTunes 7.01, and what appeared to be valid ID3V2 data.
    // May be related to thumbnails for album art included in MP3 file by iTunes. See http://mabblog.com/blog/?p=33

    var id3Data = [];
    var id3Props = [];
    for (var prop in this.id3) {
      id3Props.push(prop);
      id3Data.push(this.id3[prop]);
      // writeDebug('id3['+prop+']: '+this.id3[prop]);
    }
    ExternalInterface.call(baseJSObject+"['"+this.sID+"']._onid3",id3Props,id3Data);
    // unhook own event handler, prevent second call (can fire twice as data is received - ID3V2 at beginning, ID3V1 at end.)
    // Therefore if ID3V2 data is received, ID3V1 is ignored.
    soundObjects[this.sID].onID3 = null;
  }

  var registerOnComplete = function(sID) {
    soundObjects[sID].onSoundComplete = function() {
      ExternalInterface.call(baseJSObject+"['"+sID+"']._onfinish");
    }
  }

  var _setPosition = function(sID,nSecOffset,isPaused) {
    var s = soundObjects[sID];
    // writeDebug('_setPosition()');
    s.lastValues.position = s.position;
    s.start(nSecOffset,s.lastValues.nLoops||1); // start playing at new position
    if (isPaused) s.stop();
  }

  var _load = function(sID,sURL,bStream,bAutoPlay) {
    writeDebug('_load()');
    if (typeof bAutoPlay == 'undefined') bAutoPlay = false;
    // checkProgress();
    var s = soundObjects[sID];
    s.onID3 = onID3;
    s.onLoad = onLoad;
    s.loaded = true;
    s.loadSound(sURL,bStream);
    s.didJustBeforeFinish = false;
    if (bAutoPlay != true) {
      s.stop(); // prevent default auto-play behaviour
      writeDebug('auto-play stopped');
    } else {
      writeDebug('auto-play allowed');
    }
    registerOnComplete(sID);
  }

  var _unload = function(sID,sURL) {
    // effectively "stop" loading by loading a tiny MP3
    writeDebug('_unload()');
    var s = soundObjects[sID];
    s.onID3 = null;
    s.onLoad = null;
    s.loaded = false;
    s.loadSound(sURL,true);
    s.stop(); // prevent auto-play
    s.didJustBeforeFinish = false;
  }

  var _createSound = function(sID,justBeforeFinishOffset) {
    soundObjects[sID] = new Sound();
    var s = soundObjects[sID];
    s.didJustBeforeFinish = false;
    s.sID = sID;
    s.paused = false;
    s.loaded = false;
    s.justBeforeFinishOffset = justBeforeFinishOffset||0;
    s.lastValues = {
      bytes: 0,
      position: 0,
      nLoops: 1
    };
    sounds.push(sID);
  }

  var _stop = function(sID,bStopAll) {
    // stop this particular instance (or "all", based on parameter)
    if (bStopAll) {
      _root.stop();
    } else {
      soundObjects[sID].stop();
      soundObjects[sID].paused = false;
      soundObjects[sID].didJustBeforeFinish = false;
    }
  }

  var _start = function(sID,nLoops,nMsecOffset) {
    registerOnComplete();
    var s = soundObjects[sID];
    s.lastValues.paused = false; // reset pause if applicable
    s.lastValues.nLoops = (nLoops||1);
    s.start(nMsecOffset,nLoops);
  }

  var _pause = function(sID) {
    writeDebug('_pause()');
    var s = soundObjects[sID];
    if (!s.paused) {
      // reference current position, stop sound
      s.paused = true; 
      s.lastValues.position = s.position;
      writeDebug('_pause(): position: '+s.lastValues.position);
      s.stop();
    } else {
      // resume playing from last position
      writeDebug('resuming - playing at '+s.lastValues.position+', '+s.lastValues.nLoops+' times');
      s.paused = false;
      s.start(s.lastValues.position/1000,s.lastValues.nLoops);
    }
  }

  var _setPan = function(sID,nPan) {
    soundObjects[sID].setPan(nPan);
  }

  var _setVolume = function(sID,nVol) {
    soundObjects[sID].setVolume(nVol);
  }

  var _setPolling = function(bPolling) {
    pollingEnabled = bPolling;
    if (timer == null && pollingEnabled) {
      writeDebug('Enabling polling');
      timer = setInterval(checkProgress,timerInterval);
    } else if (timer && !pollingEnabled) {
      writeDebug('Disabling polling');
      clearInterval(timer);
      timer = null;
    }
  }

  // XML handler stuff

  var oXML = new XML();
  oXML.ignoreWhite = true;

  var parseXML = function() {
    // trace("Parsing XML");
    var xmlRoot = oXML.firstChild;
    var xmlAttr = xmlRoot.attributes;
    var oOptions = {};
    for (var i=0,j=xmlRoot.childNodes.length; i<j; i++) {
      xmlAttr = xmlRoot.childNodes[i].attributes;
      oOptions = {
        id : xmlAttr.id,
        url : xmlRoot.attributes.baseHref+xmlAttr.href,
        stream : xmlAttr.stream
      }
      ExternalInterface.call(baseJSController+".createSound",oOptions);
    }
  }

  oXML.onLoad = function(ok) {
    if (ok) {
      // trace("XML loaded.");
      // ExternalInterface.call(baseJSController+"._writeDebug","[Flash]: XML loaded.");
          writeDebug("XML Loaded");
      parseXML();
    } else {
      // trace("XML load failed.");
      // ExternalInterface.call(baseJSController+"._writeDebug","[Flash]: XML load failed.");
      writeDebug('XML load failed');
    }
  }

  // ---

  var _loadFromXML = function(sXmlUrl) {
    writeDebug("_loadFromXML("+sXmlUrl+")");
    // ExternalInterface.call(baseJSController+"._writeDebug","_loadFromXML("+sXmlUrl+")");
    // var oXmlHandler = new XMLHandler(sXmlUrl);
    writeDebug("Attempting to load XML: "+sXmlUrl);
    oXML.load(sXmlUrl);
  }

  ExternalInterface.addCallback('_load', this, _load);
  ExternalInterface.addCallback('_unload', this, _unload);
  ExternalInterface.addCallback('_stop', this, _stop);
  ExternalInterface.addCallback('_start', this, _start);
  ExternalInterface.addCallback('_pause', this, _pause);
  ExternalInterface.addCallback('_setPosition', this, _setPosition);
  ExternalInterface.addCallback('_setPan', this, _setPan);
  ExternalInterface.addCallback('_setVolume', this, _setVolume);
  ExternalInterface.addCallback('_setPolling', this, _setPolling);
  ExternalInterface.addCallback('_externalInterfaceTest', this, _externalInterfaceTest);
  ExternalInterface.addCallback('_loadFromXML', null, _loadFromXML);
  ExternalInterface.addCallback('_createSound', this, _createSound);

  }

  // entry point
  static function main(mc) {
    app = new SoundManager2();
  }

}