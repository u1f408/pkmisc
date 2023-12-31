// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: deep-purple; icon-glyph: magic;
//
// Iris' PluralKit fronters widget for Scriptable
//
// Latest version available from https://github.com/u1f408/pkmisc
//
// If you need help using this, ask in the PluralKit Discord server's
// #third-party-discussion channel - please do not open GitHub issues
// for support requests. 
//
// Licensed under CC0 / public domain - no warranties given or implied.
//

const userOptions = {
  // Replace "exmpl" here with your system ID.
  // If you provide a token below, this field
  // is ignored.
  system: "exmpl",

  // If your current fronters are private,
  // replace the word "undefined" below with
  // your PK token, surrounded by quotes.
  token: undefined,

  // If you are using a large size widget,
  // change this to true, otherwise set this
  // to false.
  isLargeWidget: false,

  // If you want to use display names, set to
  // true. Set to false to use base member names.
  useDisplayNames: true,

  // Member avatars:
  // To show as a square, set to true.
  // To show as a circle, set to "circle".
  // To disable member avatars, set to false.
  showAvatars: true,
};

//////////////////////////////////////////////
//        ALL OPTIONS ARE SET ABOVE!
// You don't need to edit anything below here!
//////////////////////////////////////////////

function timeAgo(elapsed) {
  const units = [
    {unit: "d", ms: 86400000},
    {unit: "h", ms: 3600000},
    {unit: "m", ms: 60000},
  ];

  elapsed = Math.abs(elapsed);
  let s = "";
  for (const {unit, ms} of units) {
    if (Math.abs(elapsed) >= ms) {
      let b = Math.abs(Math.floor(elapsed / ms));
      elapsed -= b * ms;
      s += b + unit;
    }
  }

  if (s === "") s = Math.floor(elapsed / 1000) + "s";
  return s;
}

function tinyStringHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash &= hash;
  }
  return hash;
}

function determineFallbackAvatar(member) {
  let avid = 0;
  if (member.uuid !== undefined) avid = tinyStringHash(member.uuid);
  return `https://cdn.discordapp.com/embed/avatars/${Math.abs(avid)%4}.png`;
}

function FronterWidget(opts) {
  this.opts = Object.assign({
    system: "exmpl",
    isLargeWidget: false,
    useDisplayNames: false,
    showAvatars: true,
    avatarSize: 24,
    avatarPlaceholder: determineFallbackAvatar,
    listCutoffDefault: 5,
    listCutoffLarge: 9,
    backgroundColor: Color.dynamic(Color.white(), Color.black()),
    textColorNormal: Color.dynamic(Color.black(), Color.white()),
    textColorDimmed: Color.gray(),
    apiBase: "https://api.pluralkit.me/v2",
  }, opts);

  if (this.opts.token !== undefined) this.opts.system = '@me';
  this.avatarSize = new Size(this.opts.avatarSize, this.opts.avatarSize);
  this.userAgent = "ScriptablePKFronters/0.2 (https://github.com/u1f408/pkmisc)";

  return this;
}

FronterWidget.prototype.fetchImage = function(url) {
  let req = new Request(url);
  req.headers = {"User-Agent": this.userAgent};
  return req.loadImage();
}

FronterWidget.prototype.fetchFronters = async function() {
  let url = this.opts.apiBase + "/systems/" + this.opts.system + "/fronters";
  let req = new Request(url);
  req.headers = {"User-Agent": this.userAgent, "Authorization": this.opts.token};

  let data = await req.loadJSON();
  if (!("members" in data))
    throw new Error(
      "Couldn't get fronters!? " +
      (this.opts.token === undefined
        ? "Invalid system ID, or current fronters are private."
        : "Your token might be invalid."));

  return data;
}

FronterWidget.prototype.fetchMemberAvatar = async function(member) {
  let url = member.webhook_avatar_url || member.avatar_url;

  try {
    if (!url) throw "noavi";
    return await this.fetchImage(url);
  } catch (ex) {
    url = typeof this.opts.avatarPlaceholder == "function"
      ? this.opts.avatarPlaceholder(member)
      : this.opts.avatarPlaceholder;
    return await this.fetchImage(url);
  }
}

FronterWidget.prototype.renderMember = async function(member, list) {
  let mel = list.addStack();
  mel.layoutHorizontally();
  mel.centerAlignContent();

  if (this.opts.showAvatars !== false) {
    let imgData = await this.fetchMemberAvatar(member);
    let img = mel.addImage(imgData);
    img.imageSize = this.avatarSize;
    img.cornerRadius = this.opts.showAvatars === "circle"
      ? Math.ceil(this.avatarSize.height / 2)
      : 3;

    mel.addSpacer(4);
  }

  let mname = this.opts.useDisplayNames
    ? member.display_name || member.name
    : member.name || member.display_name;

  let mtxt = mel.addText(mname);
  mtxt.color = this.opts.textColorNormal;

  return mel;
}

FronterWidget.prototype.renderWidget = async function() {
  let base = new ListWidget();
  base.setPadding(0, 0, 0, 0);
  base.backgroundColor = this.opts.backgroundColor;
  let stack = base.addStack();
  stack.topAlignContent();
  stack.layoutHorizontally();
  stack.setPadding(0, 0, 0, 0);

  let list = stack.addStack();
  stack.addSpacer();
  list.spacing = 2;
  list.setPadding(12, 16, 0, 0);
  list.layoutVertically();
  list.topAlignContent();

  var res;
  try {
    res = await this.fetchFronters();
  } catch (ex) {
    let etxt = list.addText(ex.message);
    return base;
  }

  const now = new Date();
  let ts = timeAgo(Date.parse(res.timestamp) - now.getTime());

  let showMore = false;
  let cutoff = this.opts.isLargeWidget
    ? this.opts.listCutoffLarge
    : this.opts.listCutoffDefault;

  if (cutoff < res.members.length) {
    cutoff = cutoff - 1;
    showMore = true;
  } else {
    cutoff = res.members.length;
  }

  for (let n = 0; n < cutoff; n++) {
    await this.renderMember(res.members[n], list);
  }

  if (showMore) {
    let mel = list.addStack();
    let mtxt = mel.addText("… and " + (res.members.length - cutoff).toString() + " more");
    mtxt.textColor = this.opts.textColorDimmed;
  }

  list.addSpacer();
  let meta = stack.addStack();
  meta.setPadding(12, 0, 0, 16);
  meta.layoutVertically();
  meta.spacing = 4;
  let mts = meta.addText(ts.toString());
  mts.textColor = this.opts.textColorDimmed;
  meta.addSpacer();

  return base;
}

let meow = new FronterWidget(userOptions);
let widget = await meow.renderWidget();
Script.setWidget(widget);
Script.complete();

// vim: set sts=0 ts=2 sw=2 et syntax=js :
