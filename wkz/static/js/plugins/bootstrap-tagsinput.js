/*
 * bootstrap-tagsinput v0.8.0
 *
 */

! function(t) {
  "use strict";
  var e = {
    tagClass: function(t) {
      return "badge badge-success"
    },
    focusClass: "focus",
    itemValue: function(t) {
      return t ? t.toString() : t
    },
    itemText: function(t) {
      return this.itemValue(t)
    },
    itemTitle: function(t) {
      return null
    },
    freeInput: !0,
    addOnBlur: !0,
    maxTags: void 0,
    maxChars: void 0,
    confirmKeys: [13, 44],
    delimiter: ",",
    delimiterRegex: null,
    cancelConfirmKeysOnEmpty: !1,
    onTagExists: function(t, e) {
      e.hide().fadeIn()
    },
    trimValue: !1,
    allowDuplicates: !1,
    triggerChange: !0
  };

  function n(e, n) {
    this.isInit = !0, this.itemsArray = [], this.$element = t(e), this.$element.hide(), this.isSelect = "SELECT" === e.tagName, this.multiple = this.isSelect && e.hasAttribute("multiple"), this.objectItems = n && n.itemValue, this.placeholderText = e.hasAttribute("placeholder") ? this.$element.attr("placeholder") : "", this.inputSize = Math.max(1, this.placeholderText.length), this.$container = t('<div class="bootstrap-tagsinput"></div>'), this.$input = t('<input type="text" placeholder="' + this.placeholderText + '"/>').appendTo(this.$container), this.$element.before(this.$container), this.build(n), this.isInit = !1
  }

  function i(t, e) {
    if ("function" != typeof t[e]) {
      var n = t[e];
      t[e] = function(t) {
        return t[n]
      }
    }
  }

  function a(t, e) {
    if ("function" != typeof t[e]) {
      var n = t[e];
      t[e] = function() {
        return n
      }
    }
  }
  n.prototype = {
    constructor: n,
    add: function(e, n, i) {
      var a = this;
      if (!(a.options.maxTags && a.itemsArray.length >= a.options.maxTags) && (!1 === e || e)) {
        if ("string" == typeof e && a.options.trimValue && (e = t.trim(e)), "object" == typeof e && !a.objectItems) throw "Can't add objects when itemValue option is not set";
        if (!e.toString().match(/^\s*$/)) {
          if (a.isSelect && !a.multiple && a.itemsArray.length > 0 && a.remove(a.itemsArray[0]), "string" == typeof e && "INPUT" === this.$element[0].tagName) {
            var o = a.options.delimiterRegex ? a.options.delimiterRegex : a.options.delimiter,
              s = e.split(o);
            if (s.length > 1) {
              for (var l = 0; l < s.length; l++) this.add(s[l], !0);
              return void(n || a.pushVal(a.options.triggerChange))
            }
          }
          var u = a.options.itemValue(e),
            p = a.options.itemText(e),
            c = a.options.tagClass(e),
            h = a.options.itemTitle(e),
            m = t.grep(a.itemsArray, function(t) {
              return a.options.itemValue(t) === u
            })[0];
          if (!m || a.options.allowDuplicates) {
            if (!(a.items().toString().length + e.length + 1 > a.options.maxInputLength)) {
              var f = t.Event("beforeItemAdd", {
                item: e,
                cancel: !1,
                options: i
              });
              if (a.$element.trigger(f), !f.cancel) {
                a.itemsArray.push(e);
                var d = t('<span class="badge ' + r(c) + (null !== h ? '" title="' + h : "") + '">' + r(p) + '<span data-role="remove"></span></span>');
                d.data("item", e), a.findInputWrapper().before(d), d.after(" ");
                var g = t('option[value="' + encodeURIComponent(u) + '"]', a.$element).length || t('option[value="' + r(u) + '"]', a.$element).length;
                if (a.isSelect && !g) {
                  var v = t("<option selected>" + r(p) + "</option>");
                  v.data("item", e), v.attr("value", u), a.$element.append(v)
                }
                n || a.pushVal(a.options.triggerChange), a.options.maxTags !== a.itemsArray.length && a.items().toString().length !== a.options.maxInputLength || a.$container.addClass("bootstrap-tagsinput-max"), t(".typeahead, .twitter-typeahead", a.$container).length && a.$input.typeahead("val", ""), this.isInit ? a.$element.trigger(t.Event("itemAddedOnInit", {
                  item: e,
                  options: i
                })) : a.$element.trigger(t.Event("itemAdded", {
                  item: e,
                  options: i
                }))
              }
            }
          } else if (a.options.onTagExists) {
            var y = t(".badge", a.$container).filter(function() {
              return t(this).data("item") === m
            });
            a.options.onTagExists(e, y)
          }
        }
      }
    },
    remove: function(e, n, i) {
      var a = this;
      if (a.objectItems && (e = (e = "object" == typeof e ? t.grep(a.itemsArray, function(t) {
          return a.options.itemValue(t) == a.options.itemValue(e)
        }) : t.grep(a.itemsArray, function(t) {
          return a.options.itemValue(t) == e
        }))[e.length - 1]), e) {
        var o = t.Event("beforeItemRemove", {
          item: e,
          cancel: !1,
          options: i
        });
        if (a.$element.trigger(o), o.cancel) return;
        t(".badge", a.$container).filter(function() {
          return t(this).data("item") === e
        }).remove(), t("option", a.$element).filter(function() {
          return t(this).data("item") === e
        }).remove(), -1 !== t.inArray(e, a.itemsArray) && a.itemsArray.splice(t.inArray(e, a.itemsArray), 1)
      }
      n || a.pushVal(a.options.triggerChange), a.options.maxTags > a.itemsArray.length && a.$container.removeClass("bootstrap-tagsinput-max"), a.$element.trigger(t.Event("itemRemoved", {
        item: e,
        options: i
      }))
    },
    removeAll: function() {
      var e = this;
      for (t(".badge", e.$container).remove(), t("option", e.$element).remove(); e.itemsArray.length > 0;) e.itemsArray.pop();
      e.pushVal(e.options.triggerChange)
    },
    refresh: function() {
      var e = this;
      t(".badge", e.$container).each(function() {
        var n = t(this),
          i = n.data("item"),
          a = e.options.itemValue(i),
          o = e.options.itemText(i),
          s = e.options.tagClass(i);
        (n.attr("class", null), n.addClass("badge " + r(s)), n.contents().filter(function() {
          return 3 == this.nodeType
        })[0].nodeValue = r(o), e.isSelect) && t("option", e.$element).filter(function() {
          return t(this).data("item") === i
        }).attr("value", a)
      })
    },
    items: function() {
      return this.itemsArray
    },
    pushVal: function() {
      var e = this,
        n = t.map(e.items(), function(t) {
          return e.options.itemValue(t).toString()
        });
      e.$element.val(n, !0), e.options.triggerChange && e.$element.trigger("change")
    },
    build: function(n) {
      var o = this;
      if (o.options = t.extend({}, e, n), o.objectItems && (o.options.freeInput = !1), i(o.options, "itemValue"), i(o.options, "itemText"), a(o.options, "tagClass"), o.options.typeahead) {
        var r = o.options.typeahead || {};
        a(r, "source"), o.$input.typeahead(t.extend({}, r, {
          source: function(e, n) {
            function i(t) {
              for (var e = [], i = 0; i < t.length; i++) {
                var r = o.options.itemText(t[i]);
                a[r] = t[i], e.push(r)
              }
              n(e)
            }
            this.map = {};
            var a = this.map,
              s = r.source(e);
            t.isFunction(s.success) ? s.success(i) : t.isFunction(s.then) ? s.then(i) : t.when(s).then(i)
          },
          updater: function(t) {
            return o.add(this.map[t]), this.map[t]
          },
          matcher: function(t) {
            return -1 !== t.toLowerCase().indexOf(this.query.trim().toLowerCase())
          },
          sorter: function(t) {
            return t.sort()
          },
          highlighter: function(t) {
            var e = new RegExp("(" + this.query + ")", "gi");
            return t.replace(e, "<strong>$1</strong>")
          }
        }))
      }
      if (o.options.typeaheadjs) {
        var l = o.options.typeaheadjs;
        t.isArray(l) || (l = [null, l]), t.fn.typeahead.apply(o.$input, l).on("typeahead:selected", t.proxy(function(t, e, n) {
          var i = 0;
          l.some(function(t, e) {
            return t.name === n && (i = e, !0)
          }), l[i].valueKey ? o.add(e[l[i].valueKey]) : o.add(e), o.$input.typeahead("val", "")
        }, o))
      }
      o.$container.on("click", t.proxy(function(t) {
        o.$element.attr("disabled") || o.$input.removeAttr("disabled"), o.$input.focus()
      }, o)), o.options.addOnBlur && o.options.freeInput && o.$input.on("focusout", t.proxy(function(e) {
        0 === t(".typeahead, .twitter-typeahead", o.$container).length && (o.add(o.$input.val()), o.$input.val(""))
      }, o)), o.$container.on({
        focusin: function() {
          o.$container.addClass(o.options.focusClass)
        },
        focusout: function() {
          o.$container.removeClass(o.options.focusClass)
        }
      }), o.$container.on("keydown", "input", t.proxy(function(e) {
        var n = t(e.target),
          i = o.findInputWrapper();
        if (o.$element.attr("disabled")) o.$input.attr("disabled", "disabled");
        else {
          switch (e.which) {
            case 8:
              if (0 === s(n[0])) {
                var a = i.prev();
                a.length && o.remove(a.data("item"))
              }
              break;
            case 46:
              if (0 === s(n[0])) {
                var r = i.next();
                r.length && o.remove(r.data("item"))
              }
              break;
            case 37:
              var l = i.prev();
              0 === n.val().length && l[0] && (l.before(i), n.focus());
              break;
            case 39:
              var u = i.next();
              0 === n.val().length && u[0] && (u.after(i), n.focus())
          }
          var p = n.val().length;
          Math.ceil(p / 5);
          n.attr("size", Math.max(this.inputSize, n.val().length))
        }
      }, o)), o.$container.on("keypress", "input", t.proxy(function(e) {
        var n = t(e.target);
        if (o.$element.attr("disabled")) o.$input.attr("disabled", "disabled");
        else {
          var i, a, r, s = n.val(),
            l = o.options.maxChars && s.length >= o.options.maxChars;
          o.options.freeInput && (i = e, a = o.options.confirmKeys, r = !1, t.each(a, function(t, e) {
            if ("number" == typeof e && i.which === e) return r = !0, !1;
            if (i.which === e.which) {
              var n = !e.hasOwnProperty("altKey") || i.altKey === e.altKey,
                a = !e.hasOwnProperty("shiftKey") || i.shiftKey === e.shiftKey,
                o = !e.hasOwnProperty("ctrlKey") || i.ctrlKey === e.ctrlKey;
              if (n && a && o) return r = !0, !1
            }
          }), r || l) && (0 !== s.length && (o.add(l ? s.substr(0, o.options.maxChars) : s), n.val("")), !1 === o.options.cancelConfirmKeysOnEmpty && e.preventDefault());
          var u = n.val().length;
          Math.ceil(u / 5);
          n.attr("size", Math.max(this.inputSize, n.val().length))
        }
      }, o)), o.$container.on("click", "[data-role=remove]", t.proxy(function(e) {
        o.$element.attr("disabled") || o.remove(t(e.target).closest(".badge").data("item"))
      }, o)), o.options.itemValue === e.itemValue && ("INPUT" === o.$element[0].tagName ? o.add(o.$element.val()) : t("option", o.$element).each(function() {
        o.add(t(this).attr("value"), !0)
      }))
    },
    destroy: function() {
      var t = this;
      t.$container.off("keypress", "input"), t.$container.off("click", "[role=remove]"), t.$container.remove(), t.$element.removeData("tagsinput"), t.$element.show()
    },
    focus: function() {
      this.$input.focus()
    },
    input: function() {
      return this.$input
    },
    findInputWrapper: function() {
      for (var e = this.$input[0], n = this.$container[0]; e && e.parentNode !== n;) e = e.parentNode;
      return t(e)
    }
  }, t.fn.tagsinput = function(e, i, a) {
    var o = [];
    return this.each(function() {
      var r = t(this).data("tagsinput");
      if (r)
        if (e || i) {
          if (void 0 !== r[e]) {
            if (3 === r[e].length && void 0 !== a) var s = r[e](i, null, a);
            else s = r[e](i);
            void 0 !== s && o.push(s)
          }
        } else o.push(r);
      else r = new n(this, e), t(this).data("tagsinput", r), o.push(r), "SELECT" === this.tagName && t("option", t(this)).attr("selected", "selected"), t(this).val(t(this).val())
    }), "string" == typeof e ? o.length > 1 ? o : o[0] : o
  }, t.fn.tagsinput.Constructor = n;
  var o = t("<div />");

  function r(t) {
    return t ? o.text(t).html() : ""
  }

  function s(t) {
    var e = 0;
    if (document.selection) {
      t.focus();
      var n = document.selection.createRange();
      n.moveStart("character", -t.value.length), e = n.text.length
    } else(t.selectionStart || "0" == t.selectionStart) && (e = t.selectionStart);
    return e
  }
  t(function() {
    t("input[data-role=tagsinput], select[multiple][data-role=tagsinput]").tagsinput()
  })
}(window.jQuery);