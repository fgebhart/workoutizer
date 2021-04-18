/*! version : 4.17.47
 =========================================================
 bootstrap-datetimejs
 https://github.com/Eonasdan/bootstrap-datetimepicker
 Copyright (c) 2015 Jonathan Peterson
 =========================================================
 */
/*
 The MIT License (MIT)

 Copyright (c) 2015 Jonathan Peterson

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
 */
/*global define:false */
/*global exports:false */
/*global require:false */
/*global jQuery:false */
/*global moment:false */

! function(e) {
  "use strict";
  if ("function" == typeof define && define.amd) define(["jquery", "moment"], e);
  else if ("object" == typeof exports) module.exports = e(require("jquery"), require("moment"));
  else {
    if ("undefined" == typeof jQuery) throw "bootstrap-datetimepicker requires jQuery to be loaded first";
    if ("undefined" == typeof moment) throw "bootstrap-datetimepicker requires Moment.js to be loaded first";
    e(jQuery, moment)
  }
}(function(e, t) {
  "use strict";
  if (!t) throw new Error("bootstrap-datetimepicker requires Moment.js to be loaded first");
  var a = function(a, n) {
    var r, i, o, s, d, l, p, c, u, f = {},
      h = !0,
      m = !1,
      y = !1,
      b = 0,
      g = [{
        clsName: "days",
        navFnc: "M",
        navStep: 1
      }, {
        clsName: "months",
        navFnc: "y",
        navStep: 1
      }, {
        clsName: "years",
        navFnc: "y",
        navStep: 10
      }, {
        clsName: "decades",
        navFnc: "y",
        navStep: 100
      }],
      w = ["days", "months", "years", "decades"],
      v = ["top", "bottom", "auto"],
      k = ["left", "right", "auto"],
      D = ["default", "top", "bottom"],
      C = {
        up: 38,
        38: "up",
        down: 40,
        40: "down",
        left: 37,
        37: "left",
        right: 39,
        39: "right",
        tab: 9,
        9: "tab",
        escape: 27,
        27: "escape",
        enter: 13,
        13: "enter",
        pageUp: 33,
        33: "pageUp",
        pageDown: 34,
        34: "pageDown",
        shift: 16,
        16: "shift",
        control: 17,
        17: "control",
        space: 32,
        32: "space",
        t: 84,
        84: "t",
        delete: 46,
        46: "delete"
      },
      x = {},
      T = function() {
        return void 0 !== t.tz && void 0 !== n.timeZone && null !== n.timeZone && "" !== n.timeZone
      },
      M = function(e) {
        var a;
        return a = void 0 === e || null === e ? t() : t.isDate(e) || t.isMoment(e) ? t(e) : T() ? t.tz(e, l, n.useStrict, n.timeZone) : t(e, l, n.useStrict), T() && a.tz(n.timeZone), a
      },
      S = function(e) {
        if ("string" != typeof e || e.length > 1) throw new TypeError("isEnabled expects a single character string parameter");
        switch (e) {
          case "y":
            return -1 !== d.indexOf("Y");
          case "M":
            return -1 !== d.indexOf("M");
          case "d":
            return -1 !== d.toLowerCase().indexOf("d");
          case "h":
          case "H":
            return -1 !== d.toLowerCase().indexOf("h");
          case "m":
            return -1 !== d.indexOf("m");
          case "s":
            return -1 !== d.indexOf("s");
          default:
            return !1
        }
      },
      O = function() {
        return S("h") || S("m") || S("s")
      },
      P = function() {
        return S("y") || S("M") || S("d")
      },
      E = function() {
        var t, a, r, i = e("<div>").addClass("timepicker-hours").append(e("<table>").addClass("table-condensed")),
          o = e("<div>").addClass("timepicker-minutes").append(e("<table>").addClass("table-condensed")),
          d = e("<div>").addClass("timepicker-seconds").append(e("<table>").addClass("table-condensed")),
          l = [(t = e("<tr>"), a = e("<tr>"), r = e("<tr>"), S("h") && (t.append(e("<td>").append(e("<a>").attr({
            href: "#",
            tabindex: "-1",
            title: n.tooltips.incrementHour
          }).addClass("btn").attr("data-action", "incrementHours").append(e("<span>").addClass(n.icons.up)))), a.append(e("<td>").append(e("<span>").addClass("timepicker-hour").attr({
            "data-time-component": "hours",
            title: n.tooltips.pickHour
          }).attr("data-action", "showHours"))), r.append(e("<td>").append(e("<a>").attr({
            href: "#",
            tabindex: "-1",
            title: n.tooltips.decrementHour
          }).addClass("btn").attr("data-action", "decrementHours").append(e("<span>").addClass(n.icons.down))))), S("m") && (S("h") && (t.append(e("<td>").addClass("separator")), a.append(e("<td>").addClass("separator").html(":")), r.append(e("<td>").addClass("separator"))), t.append(e("<td>").append(e("<a>").attr({
            href: "#",
            tabindex: "-1",
            title: n.tooltips.incrementMinute
          }).addClass("btn").attr("data-action", "incrementMinutes").append(e("<span>").addClass(n.icons.up)))), a.append(e("<td>").append(e("<span>").addClass("timepicker-minute").attr({
            "data-time-component": "minutes",
            title: n.tooltips.pickMinute
          }).attr("data-action", "showMinutes"))), r.append(e("<td>").append(e("<a>").attr({
            href: "#",
            tabindex: "-1",
            title: n.tooltips.decrementMinute
          }).addClass("btn").attr("data-action", "decrementMinutes").append(e("<span>").addClass(n.icons.down))))), S("s") && (S("m") && (t.append(e("<td>").addClass("separator")), a.append(e("<td>").addClass("separator").html(":")), r.append(e("<td>").addClass("separator"))), t.append(e("<td>").append(e("<a>").attr({
            href: "#",
            tabindex: "-1",
            title: n.tooltips.incrementSecond
          }).addClass("btn btn-link").attr("data-action", "incrementSeconds").append(e("<span>").addClass(n.icons.up)))), a.append(e("<td>").append(e("<span>").addClass("timepicker-second").attr({
            "data-time-component": "seconds",
            title: n.tooltips.pickSecond
          }).attr("data-action", "showSeconds"))), r.append(e("<td>").append(e("<a>").attr({
            href: "#",
            tabindex: "-1",
            title: n.tooltips.decrementSecond
          }).addClass("btn btn-link").attr("data-action", "decrementSeconds").append(e("<span>").addClass(n.icons.down))))), s || (t.append(e("<td>").addClass("separator")), a.append(e("<td>").append(e("<button>").addClass("btn btn-outline-primary btn-round").attr({
            "data-action": "togglePeriod",
            tabindex: "-1",
            title: n.tooltips.togglePeriod
          }))), r.append(e("<td>").addClass("separator"))), e("<div>").addClass("timepicker-picker").append(e("<table>").addClass("table-condensed").append([t, a, r])))];
        return S("h") && l.push(i), S("m") && l.push(o), S("s") && l.push(d), l
      },
      H = function() {
        var t, a, r, i = e("<div>").addClass("bootstrap-datetimepicker-widget dropdown-menu"),
          o = e("<div>").addClass("datepicker").append((a = e("<thead>").append(e("<tr>").append(e("<th>").addClass("prev").attr("data-action", "previous").append(e("<span>").addClass(n.icons.previous))).append(e("<th>").addClass("picker-switch").attr("data-action", "pickerSwitch").attr("colspan", n.calendarWeeks ? "6" : "5")).append(e("<th>").addClass("next").attr("data-action", "next").append(e("<span>").addClass(n.icons.next)))), r = e("<tbody>").append(e("<tr>").append(e("<td>").attr("colspan", n.calendarWeeks ? "8" : "7"))), [e("<div>").addClass("datepicker-days").append(e("<table>").addClass("table-condensed").append(a).append(e("<tbody>"))), e("<div>").addClass("datepicker-months").append(e("<table>").addClass("table-condensed").append(a.clone()).append(r.clone())), e("<div>").addClass("datepicker-years").append(e("<table>").addClass("table-condensed").append(a.clone()).append(r.clone())), e("<div>").addClass("datepicker-decades").append(e("<table>").addClass("table-condensed").append(a.clone()).append(r.clone()))])),
          d = e("<div>").addClass("timepicker").append(E()),
          l = e("<ul>").addClass("list-unstyled"),
          p = e("<li>").addClass("picker-switch" + (n.collapse ? " accordion-toggle" : "")).append((t = [], n.showTodayButton && t.push(e("<td>").append(e("<a>").attr({
            "data-action": "today",
            title: n.tooltips.today
          }).append(e("<span>").addClass(n.icons.today)))), !n.sideBySide && P() && O() && t.push(e("<td>").append(e("<a>").attr({
            "data-action": "togglePicker",
            title: n.tooltips.selectTime
          }).append(e("<span>").addClass(n.icons.time)))), n.showClear && t.push(e("<td>").append(e("<a>").attr({
            "data-action": "clear",
            title: n.tooltips.clear
          }).append(e("<span>").addClass(n.icons.clear)))), n.showClose && t.push(e("<td>").append(e("<a>").attr({
            "data-action": "close",
            title: n.tooltips.close
          }).append(e("<span>").addClass(n.icons.close)))), e("<table>").addClass("table-condensed").append(e("<tbody>").append(e("<tr>").append(t)))));
        return n.inline && i.removeClass("dropdown-menu"), s && i.addClass("usetwentyfour"), S("s") && !s && i.addClass("wider"), n.sideBySide && P() && O() ? (i.addClass("timepicker-sbs"), "top" === n.toolbarPlacement && i.append(p), i.append(e("<div>").addClass("row").append(o.addClass("col-md-6")).append(d.addClass("col-md-6"))), "bottom" === n.toolbarPlacement && i.append(p), i) : ("top" === n.toolbarPlacement && l.append(p), P() && l.append(e("<li>").addClass(n.collapse && O() ? "collapse show" : "").append(o)), "default" === n.toolbarPlacement && l.append(p), O() && l.append(e("<li>").addClass(n.collapse && P() ? "collapse" : "").append(d)), "bottom" === n.toolbarPlacement && l.append(p), i.append(l))
      },
      I = function() {
        var t, r = (m || a).position(),
          i = (m || a).offset(),
          o = n.widgetPositioning.vertical,
          s = n.widgetPositioning.horizontal;
        if (n.widgetParent) t = n.widgetParent.append(y);
        else if (a.is("input")) t = a.after(y).parent();
        else {
          if (n.inline) return void(t = a.append(y));
          t = a, a.children().first().after(y)
        }
        if ("auto" === o && (o = i.top + 1.5 * y.height() >= e(window).height() + e(window).scrollTop() && y.height() + a.outerHeight() < i.top ? "top" : "bottom"), "auto" === s && (s = t.width() < i.left + y.outerWidth() / 2 && i.left + y.outerWidth() > e(window).width() ? "right" : "left"), "top" === o ? y.addClass("top").removeClass("bottom") : y.addClass("bottom").removeClass("top"), "right" === s ? y.addClass("pull-right") : y.removeClass("pull-right"), "static" === t.css("position") && (t = t.parents().filter(function() {
            return "static" !== e(this).css("position")
          }).first()), 0 === t.length) throw new Error("datetimepicker component should be placed within a non-static positioned container");
        y.css({
          top: "top" === o ? "auto" : r.top + a.outerHeight(),
          bottom: "top" === o ? t.outerHeight() - (t === a ? 0 : r.top) : "auto",
          left: "left" === s ? t === a ? 0 : r.left : "auto",
          right: "left" === s ? "auto" : t.outerWidth() - a.outerWidth() - (t === a ? 0 : r.left)
        }), setTimeout(function() {
          y.addClass("open")
        }, 180)
      },
      Y = function(e) {
        "dp.change" === e.type && (e.date && e.date.isSame(e.oldDate) || !e.date && !e.oldDate) || a.trigger(e)
      },
      q = function(e) {
        "y" === e && (e = "YYYY"), Y({
          type: "dp.update",
          change: e,
          viewDate: i.clone()
        })
      },
      B = function(e) {
        y && (e && (p = Math.max(b, Math.min(3, p + e))), y.find(".datepicker > div").hide().filter(".datepicker-" + g[p].clsName).show())
      },
      j = function(t, a) {
        if (!t.isValid()) return !1;
        if (n.disabledDates && "d" === a && (r = t, !0 === n.disabledDates[r.format("YYYY-MM-DD")])) return !1;
        var r, i, o, s;
        if (n.enabledDates && "d" === a && (i = t, !0 !== n.enabledDates[i.format("YYYY-MM-DD")])) return !1;
        if (n.minDate && t.isBefore(n.minDate, a)) return !1;
        if (n.maxDate && t.isAfter(n.maxDate, a)) return !1;
        if (n.daysOfWeekDisabled && "d" === a && -1 !== n.daysOfWeekDisabled.indexOf(t.day())) return !1;
        if (n.disabledHours && ("h" === a || "m" === a || "s" === a) && (o = t, !0 === n.disabledHours[o.format("H")])) return !1;
        if (n.enabledHours && ("h" === a || "m" === a || "s" === a) && (s = t, !0 !== n.enabledHours[s.format("H")])) return !1;
        if (n.disabledTimeIntervals && ("h" === a || "m" === a || "s" === a)) {
          var d = !1;
          if (e.each(n.disabledTimeIntervals, function() {
              if (t.isBetween(this[0], this[1])) return d = !0, !1
            }), d) return !1
        }
        return !0
      },
      A = function() {
        var a, o, s, d = y.find(".datepicker-days"),
          l = d.find("th"),
          p = [],
          c = [];
        if (P()) {
          for (l.eq(0).find("span").attr("title", n.tooltips.prevMonth), l.eq(1).attr("title", n.tooltips.selectMonth), l.eq(2).find("span").attr("title", n.tooltips.nextMonth), d.find(".disabled").removeClass("disabled"), l.eq(1).text(i.format(n.dayViewHeaderFormat)), j(i.clone().subtract(1, "M"), "M") || l.eq(0).addClass("disabled"), j(i.clone().add(1, "M"), "M") || l.eq(2).addClass("disabled"), a = i.clone().startOf("M").startOf("w").startOf("d"), s = 0; s < 42; s++) 0 === a.weekday() && (o = e("<tr>"), n.calendarWeeks && o.append('<td class="cw">' + a.week() + "</td>"), p.push(o)), c = ["day"], a.isBefore(i, "M") && c.push("old"), a.isAfter(i, "M") && c.push("new"), a.isSame(r, "d") && !h && c.push("active"), j(a, "d") || c.push("disabled"), a.isSame(M(), "d") && c.push("today"), 0 !== a.day() && 6 !== a.day() || c.push("weekend"), Y({
            type: "dp.classify",
            date: a,
            classNames: c
          }), o.append('<td data-action="selectDay" data-day="' + a.format("L") + '" class="' + c.join(" ") + '"><div>' + a.date() + "</div></td>"), a.add(1, "d");
          var u, f, m;
          d.find("tbody").empty().append(p), u = y.find(".datepicker-months"), f = u.find("th"), m = u.find("tbody").find("span"), f.eq(0).find("span").attr("title", n.tooltips.prevYear), f.eq(1).attr("title", n.tooltips.selectYear), f.eq(2).find("span").attr("title", n.tooltips.nextYear), u.find(".disabled").removeClass("disabled"), j(i.clone().subtract(1, "y"), "y") || f.eq(0).addClass("disabled"), f.eq(1).text(i.year()), j(i.clone().add(1, "y"), "y") || f.eq(2).addClass("disabled"), m.removeClass("active"), r.isSame(i, "y") && !h && m.eq(r.month()).addClass("active"), m.each(function(t) {
              j(i.clone().month(t), "M") || e(this).addClass("disabled")
            }),
            function() {
              var e = y.find(".datepicker-years"),
                t = e.find("th"),
                a = i.clone().subtract(5, "y"),
                o = i.clone().add(6, "y"),
                s = "";
              for (t.eq(0).find("span").attr("title", n.tooltips.prevDecade), t.eq(1).attr("title", n.tooltips.selectDecade), t.eq(2).find("span").attr("title", n.tooltips.nextDecade), e.find(".disabled").removeClass("disabled"), n.minDate && n.minDate.isAfter(a, "y") && t.eq(0).addClass("disabled"), t.eq(1).text(a.year() + "-" + o.year()), n.maxDate && n.maxDate.isBefore(o, "y") && t.eq(2).addClass("disabled"); !a.isAfter(o, "y");) s += '<span data-action="selectYear" class="year' + (a.isSame(r, "y") && !h ? " active" : "") + (j(a, "y") ? "" : " disabled") + '">' + a.year() + "</span>", a.add(1, "y");
              e.find("td").html(s)
            }(),
            function() {
              var e, a = y.find(".datepicker-decades"),
                o = a.find("th"),
                s = t({
                  y: i.year() - i.year() % 100 - 1
                }),
                d = s.clone().add(100, "y"),
                l = s.clone(),
                p = !1,
                c = !1,
                u = "";
              for (o.eq(0).find("span").attr("title", n.tooltips.prevCentury), o.eq(2).find("span").attr("title", n.tooltips.nextCentury), a.find(".disabled").removeClass("disabled"), (s.isSame(t({
                  y: 1900
                })) || n.minDate && n.minDate.isAfter(s, "y")) && o.eq(0).addClass("disabled"), o.eq(1).text(s.year() + "-" + d.year()), (s.isSame(t({
                  y: 2e3
                })) || n.maxDate && n.maxDate.isBefore(d, "y")) && o.eq(2).addClass("disabled"); !s.isAfter(d, "y");) e = s.year() + 12, p = n.minDate && n.minDate.isAfter(s, "y") && n.minDate.year() <= e, c = n.maxDate && n.maxDate.isAfter(s, "y") && n.maxDate.year() <= e, u += '<span data-action="selectDecade" class="decade' + (r.isAfter(s) && r.year() <= e ? " active" : "") + (j(s, "y") || p || c ? "" : " disabled") + '" data-selection="' + (s.year() + 6) + '">' + (s.year() + 1) + " - " + (s.year() + 12) + "</span>", s.add(12, "y");
              u += "<span></span><span></span><span></span>", a.find("td").html(u), o.eq(1).text(l.year() + 1 + "-" + s.year())
            }()
        }
      },
      F = function() {
        var t, a, o = y.find(".timepicker span[data-time-component]");
        s || (t = y.find(".timepicker [data-action=togglePeriod]"), a = r.clone().add(r.hours() >= 12 ? -12 : 12, "h"), t.text(r.format("A")), j(a, "h") ? t.removeClass("disabled") : t.addClass("disabled")), o.filter("[data-time-component=hours]").text(r.format(s ? "HH" : "hh")), o.filter("[data-time-component=minutes]").text(r.format("mm")), o.filter("[data-time-component=seconds]").text(r.format("ss")),
          function() {
            var t = y.find(".timepicker-hours table"),
              a = i.clone().startOf("d"),
              n = [],
              r = e("<tr>");
            for (i.hour() > 11 && !s && a.hour(12); a.isSame(i, "d") && (s || i.hour() < 12 && a.hour() < 12 || i.hour() > 11);) a.hour() % 4 == 0 && (r = e("<tr>"), n.push(r)), r.append('<td data-action="selectHour" class="hour' + (j(a, "h") ? "" : " disabled") + '"><div>' + a.format(s ? "HH" : "hh") + "</div></td>"), a.add(1, "h");
            t.empty().append(n)
          }(),
          function() {
            for (var t = y.find(".timepicker-minutes table"), a = i.clone().startOf("h"), r = [], o = e("<tr>"), s = 1 === n.stepping ? 5 : n.stepping; i.isSame(a, "h");) a.minute() % (4 * s) == 0 && (o = e("<tr>"), r.push(o)), o.append('<td data-action="selectMinute" class="minute' + (j(a, "m") ? "" : " disabled") + '"><div>' + a.format("mm") + "</div></td>"), a.add(s, "m");
            t.empty().append(r)
          }(),
          function() {
            for (var t = y.find(".timepicker-seconds table"), a = i.clone().startOf("m"), n = [], r = e("<tr>"); i.isSame(a, "m");) a.second() % 20 == 0 && (r = e("<tr>"), n.push(r)), r.append('<td data-action="selectSecond" class="second' + (j(a, "s") ? "" : " disabled") + '"><div>' + a.format("ss") + "</div></td>"), a.add(5, "s");
            t.empty().append(n)
          }()
      },
      L = function() {
        y && (A(), F())
      },
      W = function(e) {
        var t = h ? null : r;
        if (!e) return h = !0, o.val(""), a.data("date", ""), Y({
          type: "dp.change",
          date: !1,
          oldDate: t
        }), void L();
        if (e = e.clone().locale(n.locale), T() && e.tz(n.timeZone), 1 !== n.stepping)
          for (e.minutes(Math.round(e.minutes() / n.stepping) * n.stepping).seconds(0); n.minDate && e.isBefore(n.minDate);) e.add(n.stepping, "minutes");
        j(e) ? (i = (r = e).clone(), o.val(r.format(d)), a.data("date", r.format(d)), h = !1, L(), Y({
          type: "dp.change",
          date: r.clone(),
          oldDate: t
        })) : (n.keepInvalid ? Y({
          type: "dp.change",
          date: e,
          oldDate: t
        }) : o.val(h ? "" : r.format(d)), Y({
          type: "dp.error",
          date: e,
          oldDate: t
        }))
      },
      z = function() {
        var t = !1;
        return y ? (y.find(".collapse").each(function() {
          var a = e(this).data("collapse");
          return !a || !a.transitioning || (t = !0, !1)
        }), t ? f : (m && m.hasClass("btn") && m.toggleClass("active"), e(window).off("resize", I), y.off("click", "[data-action]"), y.off("mousedown", !1), y.removeClass("open"), void setTimeout(function() {
          return y.remove(), y.hide(), y = !1, Y({
            type: "dp.hide",
            date: r.clone()
          }), o.blur(), p = 0, i = r.clone(), f
        }, 400))) : f
      },
      N = function() {
        W(null)
      },
      V = function(e) {
        return void 0 === n.parseInputDate ? (!t.isMoment(e) || e instanceof Date) && (e = M(e)) : e = n.parseInputDate(e), e
      },
      Z = {
        next: function() {
          var e = g[p].navFnc;
          i.add(g[p].navStep, e), A(), q(e)
        },
        previous: function() {
          var e = g[p].navFnc;
          i.subtract(g[p].navStep, e), A(), q(e)
        },
        pickerSwitch: function() {
          B(1)
        },
        selectMonth: function(t) {
          var a = e(t.target).closest("tbody").find("span").index(e(t.target));
          i.month(a), p === b ? (W(r.clone().year(i.year()).month(i.month())), n.inline || z()) : (B(-1), A()), q("M")
        },
        selectYear: function(t) {
          var a = parseInt(e(t.target).text(), 10) || 0;
          i.year(a), p === b ? (W(r.clone().year(i.year())), n.inline || z()) : (B(-1), A()), q("YYYY")
        },
        selectDecade: function(t) {
          var a = parseInt(e(t.target).data("selection"), 10) || 0;
          i.year(a), p === b ? (W(r.clone().year(i.year())), n.inline || z()) : (B(-1), A()), q("YYYY")
        },
        selectDay: function(t) {
          var a = i.clone();
          e(t.target).is(".old") && a.subtract(1, "M"), e(t.target).is(".new") && a.add(1, "M"), W(a.date(parseInt(e(t.target).text(), 10))), O() || n.keepOpen || n.inline || z()
        },
        incrementHours: function() {
          var e = r.clone().add(1, "h");
          j(e, "h") && W(e)
        },
        incrementMinutes: function() {
          var e = r.clone().add(n.stepping, "m");
          j(e, "m") && W(e)
        },
        incrementSeconds: function() {
          var e = r.clone().add(1, "s");
          j(e, "s") && W(e)
        },
        decrementHours: function() {
          var e = r.clone().subtract(1, "h");
          j(e, "h") && W(e)
        },
        decrementMinutes: function() {
          var e = r.clone().subtract(n.stepping, "m");
          j(e, "m") && W(e)
        },
        decrementSeconds: function() {
          var e = r.clone().subtract(1, "s");
          j(e, "s") && W(e)
        },
        togglePeriod: function() {
          W(r.clone().add(r.hours() >= 12 ? -12 : 12, "h"))
        },
        togglePicker: function(t) {
          var a, r = e(t.target),
            i = r.closest("ul"),
            o = i.find(".show"),
            s = i.find(".collapse:not(.show)");
          if (o && o.length) {
            if ((a = o.data("collapse")) && a.transitioning) return;
            o.collapse ? (o.collapse("hide"), s.collapse("show")) : (o.removeClass("show"), s.addClass("show")), r.is("span") ? r.toggleClass(n.icons.time + " " + n.icons.date) : r.find("span").toggleClass(n.icons.time + " " + n.icons.date)
          }
        },
        showPicker: function() {
          y.find(".timepicker > div:not(.timepicker-picker)").hide(), y.find(".timepicker .timepicker-picker").show()
        },
        showHours: function() {
          y.find(".timepicker .timepicker-picker").hide(), y.find(".timepicker .timepicker-hours").show()
        },
        showMinutes: function() {
          y.find(".timepicker .timepicker-picker").hide(), y.find(".timepicker .timepicker-minutes").show()
        },
        showSeconds: function() {
          y.find(".timepicker .timepicker-picker").hide(), y.find(".timepicker .timepicker-seconds").show()
        },
        selectHour: function(t) {
          var a = parseInt(e(t.target).text(), 10);
          s || (r.hours() >= 12 ? 12 !== a && (a += 12) : 12 === a && (a = 0)), W(r.clone().hours(a)), Z.showPicker.call(f)
        },
        selectMinute: function(t) {
          W(r.clone().minutes(parseInt(e(t.target).text(), 10))), Z.showPicker.call(f)
        },
        selectSecond: function(t) {
          W(r.clone().seconds(parseInt(e(t.target).text(), 10))), Z.showPicker.call(f)
        },
        clear: N,
        today: function() {
          var e = M();
          j(e, "d") && W(e)
        },
        close: z
      },
      R = function(t) {
        return !e(t.currentTarget).is(".disabled") && (Z[e(t.currentTarget).data("action")].apply(f, arguments), !1)
      },
      Q = function() {
        var t;
        return o.prop("disabled") || !n.ignoreReadonly && o.prop("readonly") || y ? f : (void 0 !== o.val() && 0 !== o.val().trim().length ? W(V(o.val().trim())) : h && n.useCurrent && (n.inline || o.is("input") && 0 === o.val().trim().length) && (t = M(), "string" == typeof n.useCurrent && (t = {
          year: function(e) {
            return e.month(0).date(1).hours(0).seconds(0).minutes(0)
          },
          month: function(e) {
            return e.date(1).hours(0).seconds(0).minutes(0)
          },
          day: function(e) {
            return e.hours(0).seconds(0).minutes(0)
          },
          hour: function(e) {
            return e.seconds(0).minutes(0)
          },
          minute: function(e) {
            return e.seconds(0)
          }
        } [n.useCurrent](t)), W(t)), y = H(), function() {
          var t = e("<tr>"),
            a = i.clone().startOf("w").startOf("d");
          for (!0 === n.calendarWeeks && t.append(e("<th>").addClass("cw").text("#")); a.isBefore(i.clone().endOf("w"));) t.append(e("<th>").addClass("dow").text(a.format("dd"))), a.add(1, "d");
          y.find(".datepicker-days thead").append(t)
        }(), function() {
          for (var t = [], a = i.clone().startOf("y").startOf("d"); a.isSame(i, "y");) t.push(e("<span>").attr("data-action", "selectMonth").addClass("month").text(a.format("MMM"))), a.add(1, "M");
          y.find(".datepicker-months td").empty().append(t)
        }(), y.find(".timepicker-hours").hide(), y.find(".timepicker-minutes").hide(), y.find(".timepicker-seconds").hide(), L(), B(), e(window).on("resize", I), y.on("click", "[data-action]", R), y.on("mousedown", !1), m && m.hasClass("btn") && m.toggleClass("active"), I(), y.show(), n.focusOnShow && !o.is(":focus") && o.focus(), Y({
          type: "dp.show"
        }), f)
      },
      U = function() {
        return y ? z() : Q()
      },
      G = function(e) {
        var t, a, r, i, o = null,
          s = [],
          d = {},
          l = e.which;
        x[l] = "p";
        for (t in x) x.hasOwnProperty(t) && "p" === x[t] && (s.push(t), parseInt(t, 10) !== l && (d[t] = !0));
        for (t in n.keyBinds)
          if (n.keyBinds.hasOwnProperty(t) && "function" == typeof n.keyBinds[t] && (r = t.split(" ")).length === s.length && C[l] === r[r.length - 1]) {
            for (i = !0, a = r.length - 2; a >= 0; a--)
              if (!(C[r[a]] in d)) {
                i = !1;
                break
              } if (i) {
              o = n.keyBinds[t];
              break
            }
          } o && (o.call(f, y), e.stopPropagation(), e.preventDefault())
      },
      J = function(e) {
        x[e.which] = "r", e.stopPropagation(), e.preventDefault()
      },
      K = function(t) {
        var a = e(t.target).val().trim(),
          n = a ? V(a) : null;
        return W(n), t.stopImmediatePropagation(), !1
      },
      X = function(t) {
        var a = {};
        return e.each(t, function() {
          var e = V(this);
          e.isValid() && (a[e.format("YYYY-MM-DD")] = !0)
        }), !!Object.keys(a).length && a
      },
      $ = function(t) {
        var a = {};
        return e.each(t, function() {
          a[this] = !0
        }), !!Object.keys(a).length && a
      },
      _ = function() {
        var e = n.format || "L LT";
        d = e.replace(/(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g, function(e) {
          return (r.localeData().longDateFormat(e) || e).replace(/(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g, function(e) {
            return r.localeData().longDateFormat(e) || e
          })
        }), (l = n.extraFormats ? n.extraFormats.slice() : []).indexOf(e) < 0 && l.indexOf(d) < 0 && l.push(d), s = d.toLowerCase().indexOf("a") < 1 && d.replace(/\[.*?\]/g, "").indexOf("h") < 1, S("y") && (b = 2), S("M") && (b = 1), S("d") && (b = 0), p = Math.max(b, p), h || W(r)
      };
    if (f.destroy = function() {
        z(), o.off({
          change: K,
          blur: blur,
          keydown: G,
          keyup: J,
          focus: n.allowInputToggle ? z : ""
        }), a.is("input") ? o.off({
          focus: Q
        }) : m && (m.off("click", U), m.off("mousedown", !1)), a.removeData("DateTimePicker"), a.removeData("date")
      }, f.toggle = U, f.show = Q, f.hide = z, f.disable = function() {
        return z(), m && m.hasClass("btn") && m.addClass("disabled"), o.prop("disabled", !0), f
      }, f.enable = function() {
        return m && m.hasClass("btn") && m.removeClass("disabled"), o.prop("disabled", !1), f
      }, f.ignoreReadonly = function(e) {
        if (0 === arguments.length) return n.ignoreReadonly;
        if ("boolean" != typeof e) throw new TypeError("ignoreReadonly () expects a boolean parameter");
        return n.ignoreReadonly = e, f
      }, f.options = function(t) {
        if (0 === arguments.length) return e.extend(!0, {}, n);
        if (!(t instanceof Object)) throw new TypeError("options() options parameter should be an object");
        return e.extend(!0, n, t), e.each(n, function(e, t) {
          if (void 0 === f[e]) throw new TypeError("option " + e + " is not recognized!");
          f[e](t)
        }), f
      }, f.date = function(e) {
        if (0 === arguments.length) return h ? null : r.clone();
        if (!(null === e || "string" == typeof e || t.isMoment(e) || e instanceof Date)) throw new TypeError("date() parameter must be one of [null, string, moment or Date]");
        return W(null === e ? null : V(e)), f
      }, f.format = function(e) {
        if (0 === arguments.length) return n.format;
        if ("string" != typeof e && ("boolean" != typeof e || !1 !== e)) throw new TypeError("format() expects a string or boolean:false parameter " + e);
        return n.format = e, d && _(), f
      }, f.timeZone = function(e) {
        if (0 === arguments.length) return n.timeZone;
        if ("string" != typeof e) throw new TypeError("newZone() expects a string parameter");
        return n.timeZone = e, f
      }, f.dayViewHeaderFormat = function(e) {
        if (0 === arguments.length) return n.dayViewHeaderFormat;
        if ("string" != typeof e) throw new TypeError("dayViewHeaderFormat() expects a string parameter");
        return n.dayViewHeaderFormat = e, f
      }, f.extraFormats = function(e) {
        if (0 === arguments.length) return n.extraFormats;
        if (!1 !== e && !(e instanceof Array)) throw new TypeError("extraFormats() expects an array or false parameter");
        return n.extraFormats = e, l && _(), f
      }, f.disabledDates = function(t) {
        if (0 === arguments.length) return n.disabledDates ? e.extend({}, n.disabledDates) : n.disabledDates;
        if (!t) return n.disabledDates = !1, L(), f;
        if (!(t instanceof Array)) throw new TypeError("disabledDates() expects an array parameter");
        return n.disabledDates = X(t), n.enabledDates = !1, L(), f
      }, f.enabledDates = function(t) {
        if (0 === arguments.length) return n.enabledDates ? e.extend({}, n.enabledDates) : n.enabledDates;
        if (!t) return n.enabledDates = !1, L(), f;
        if (!(t instanceof Array)) throw new TypeError("enabledDates() expects an array parameter");
        return n.enabledDates = X(t), n.disabledDates = !1, L(), f
      }, f.daysOfWeekDisabled = function(e) {
        if (0 === arguments.length) return n.daysOfWeekDisabled.splice(0);
        if ("boolean" == typeof e && !e) return n.daysOfWeekDisabled = !1, L(), f;
        if (!(e instanceof Array)) throw new TypeError("daysOfWeekDisabled() expects an array parameter");
        if (n.daysOfWeekDisabled = e.reduce(function(e, t) {
            return (t = parseInt(t, 10)) > 6 || t < 0 || isNaN(t) ? e : (-1 === e.indexOf(t) && e.push(t), e)
          }, []).sort(), n.useCurrent && !n.keepInvalid) {
          for (var t = 0; !j(r, "d");) {
            if (r.add(1, "d"), 31 === t) throw "Tried 31 times to find a valid date";
            t++
          }
          W(r)
        }
        return L(), f
      }, f.maxDate = function(e) {
        if (0 === arguments.length) return n.maxDate ? n.maxDate.clone() : n.maxDate;
        if ("boolean" == typeof e && !1 === e) return n.maxDate = !1, L(), f;
        "string" == typeof e && ("now" !== e && "moment" !== e || (e = M()));
        var t = V(e);
        if (!t.isValid()) throw new TypeError("maxDate() Could not parse date parameter: " + e);
        if (n.minDate && t.isBefore(n.minDate)) throw new TypeError("maxDate() date parameter is before options.minDate: " + t.format(d));
        return n.maxDate = t, n.useCurrent && !n.keepInvalid && r.isAfter(e) && W(n.maxDate), i.isAfter(t) && (i = t.clone().subtract(n.stepping, "m")), L(), f
      }, f.minDate = function(e) {
        if (0 === arguments.length) return n.minDate ? n.minDate.clone() : n.minDate;
        if ("boolean" == typeof e && !1 === e) return n.minDate = !1, L(), f;
        "string" == typeof e && ("now" !== e && "moment" !== e || (e = M()));
        var t = V(e);
        if (!t.isValid()) throw new TypeError("minDate() Could not parse date parameter: " + e);
        if (n.maxDate && t.isAfter(n.maxDate)) throw new TypeError("minDate() date parameter is after options.maxDate: " + t.format(d));
        return n.minDate = t, n.useCurrent && !n.keepInvalid && r.isBefore(e) && W(n.minDate), i.isBefore(t) && (i = t.clone().add(n.stepping, "m")), L(), f
      }, f.defaultDate = function(e) {
        if (0 === arguments.length) return n.defaultDate ? n.defaultDate.clone() : n.defaultDate;
        if (!e) return n.defaultDate = !1, f;
        "string" == typeof e && (e = "now" === e || "moment" === e ? M() : M(e));
        var t = V(e);
        if (!t.isValid()) throw new TypeError("defaultDate() Could not parse date parameter: " + e);
        if (!j(t)) throw new TypeError("defaultDate() date passed is invalid according to component setup validations");
        return n.defaultDate = t, (n.defaultDate && n.inline || "" === o.val().trim()) && W(n.defaultDate), f
      }, f.locale = function(e) {
        if (0 === arguments.length) return n.locale;
        if (!t.localeData(e)) throw new TypeError("locale() locale " + e + " is not loaded from moment locales!");
        return n.locale = e, r.locale(n.locale), i.locale(n.locale), d && _(), y && (z(), Q()), f
      }, f.stepping = function(e) {
        return 0 === arguments.length ? n.stepping : (e = parseInt(e, 10), (isNaN(e) || e < 1) && (e = 1), n.stepping = e, f)
      }, f.useCurrent = function(e) {
        var t = ["year", "month", "day", "hour", "minute"];
        if (0 === arguments.length) return n.useCurrent;
        if ("boolean" != typeof e && "string" != typeof e) throw new TypeError("useCurrent() expects a boolean or string parameter");
        if ("string" == typeof e && -1 === t.indexOf(e.toLowerCase())) throw new TypeError("useCurrent() expects a string parameter of " + t.join(", "));
        return n.useCurrent = e, f
      }, f.collapse = function(e) {
        if (0 === arguments.length) return n.collapse;
        if ("boolean" != typeof e) throw new TypeError("collapse() expects a boolean parameter");
        return n.collapse === e ? f : (n.collapse = e, y && (z(), Q()), f)
      }, f.icons = function(t) {
        if (0 === arguments.length) return e.extend({}, n.icons);
        if (!(t instanceof Object)) throw new TypeError("icons() expects parameter to be an Object");
        return e.extend(n.icons, t), y && (z(), Q()), f
      }, f.tooltips = function(t) {
        if (0 === arguments.length) return e.extend({}, n.tooltips);
        if (!(t instanceof Object)) throw new TypeError("tooltips() expects parameter to be an Object");
        return e.extend(n.tooltips, t), y && (z(), Q()), f
      }, f.useStrict = function(e) {
        if (0 === arguments.length) return n.useStrict;
        if ("boolean" != typeof e) throw new TypeError("useStrict() expects a boolean parameter");
        return n.useStrict = e, f
      }, f.sideBySide = function(e) {
        if (0 === arguments.length) return n.sideBySide;
        if ("boolean" != typeof e) throw new TypeError("sideBySide() expects a boolean parameter");
        return n.sideBySide = e, y && (z(), Q()), f
      }, f.viewMode = function(e) {
        if (0 === arguments.length) return n.viewMode;
        if ("string" != typeof e) throw new TypeError("viewMode() expects a string parameter");
        if (-1 === w.indexOf(e)) throw new TypeError("viewMode() parameter must be one of (" + w.join(", ") + ") value");
        return n.viewMode = e, p = Math.max(w.indexOf(e), b), B(), f
      }, f.toolbarPlacement = function(e) {
        if (0 === arguments.length) return n.toolbarPlacement;
        if ("string" != typeof e) throw new TypeError("toolbarPlacement() expects a string parameter");
        if (-1 === D.indexOf(e)) throw new TypeError("toolbarPlacement() parameter must be one of (" + D.join(", ") + ") value");
        return n.toolbarPlacement = e, y && (z(), Q()), f
      }, f.widgetPositioning = function(t) {
        if (0 === arguments.length) return e.extend({}, n.widgetPositioning);
        if ("[object Object]" !== {}.toString.call(t)) throw new TypeError("widgetPositioning() expects an object variable");
        if (t.horizontal) {
          if ("string" != typeof t.horizontal) throw new TypeError("widgetPositioning() horizontal variable must be a string");
          if (t.horizontal = t.horizontal.toLowerCase(), -1 === k.indexOf(t.horizontal)) throw new TypeError("widgetPositioning() expects horizontal parameter to be one of (" + k.join(", ") + ")");
          n.widgetPositioning.horizontal = t.horizontal
        }
        if (t.vertical) {
          if ("string" != typeof t.vertical) throw new TypeError("widgetPositioning() vertical variable must be a string");
          if (t.vertical = t.vertical.toLowerCase(), -1 === v.indexOf(t.vertical)) throw new TypeError("widgetPositioning() expects vertical parameter to be one of (" + v.join(", ") + ")");
          n.widgetPositioning.vertical = t.vertical
        }
        return L(), f
      }, f.calendarWeeks = function(e) {
        if (0 === arguments.length) return n.calendarWeeks;
        if ("boolean" != typeof e) throw new TypeError("calendarWeeks() expects parameter to be a boolean value");
        return n.calendarWeeks = e, L(), f
      }, f.showTodayButton = function(e) {
        if (0 === arguments.length) return n.showTodayButton;
        if ("boolean" != typeof e) throw new TypeError("showTodayButton() expects a boolean parameter");
        return n.showTodayButton = e, y && (z(), Q()), f
      }, f.showClear = function(e) {
        if (0 === arguments.length) return n.showClear;
        if ("boolean" != typeof e) throw new TypeError("showClear() expects a boolean parameter");
        return n.showClear = e, y && (z(), Q()), f
      }, f.widgetParent = function(t) {
        if (0 === arguments.length) return n.widgetParent;
        if ("string" == typeof t && (t = e(t)), null !== t && "string" != typeof t && !(t instanceof e)) throw new TypeError("widgetParent() expects a string or a jQuery object parameter");
        return n.widgetParent = t, y && (z(), Q()), f
      }, f.keepOpen = function(e) {
        if (0 === arguments.length) return n.keepOpen;
        if ("boolean" != typeof e) throw new TypeError("keepOpen() expects a boolean parameter");
        return n.keepOpen = e, f
      }, f.focusOnShow = function(e) {
        if (0 === arguments.length) return n.focusOnShow;
        if ("boolean" != typeof e) throw new TypeError("focusOnShow() expects a boolean parameter");
        return n.focusOnShow = e, f
      }, f.inline = function(e) {
        if (0 === arguments.length) return n.inline;
        if ("boolean" != typeof e) throw new TypeError("inline() expects a boolean parameter");
        return n.inline = e, f
      }, f.clear = function() {
        return N(), f
      }, f.keyBinds = function(e) {
        return 0 === arguments.length ? n.keyBinds : (n.keyBinds = e, f)
      }, f.getMoment = function(e) {
        return M(e)
      }, f.debug = function(e) {
        if ("boolean" != typeof e) throw new TypeError("debug() expects a boolean parameter");
        return n.debug = e, f
      }, f.allowInputToggle = function(e) {
        if (0 === arguments.length) return n.allowInputToggle;
        if ("boolean" != typeof e) throw new TypeError("allowInputToggle() expects a boolean parameter");
        return n.allowInputToggle = e, f
      }, f.showClose = function(e) {
        if (0 === arguments.length) return n.showClose;
        if ("boolean" != typeof e) throw new TypeError("showClose() expects a boolean parameter");
        return n.showClose = e, f
      }, f.keepInvalid = function(e) {
        if (0 === arguments.length) return n.keepInvalid;
        if ("boolean" != typeof e) throw new TypeError("keepInvalid() expects a boolean parameter");
        return n.keepInvalid = e, f
      }, f.datepickerInput = function(e) {
        if (0 === arguments.length) return n.datepickerInput;
        if ("string" != typeof e) throw new TypeError("datepickerInput() expects a string parameter");
        return n.datepickerInput = e, f
      }, f.parseInputDate = function(e) {
        if (0 === arguments.length) return n.parseInputDate;
        if ("function" != typeof e) throw new TypeError("parseInputDate() sholud be as function");
        return n.parseInputDate = e, f
      }, f.disabledTimeIntervals = function(t) {
        if (0 === arguments.length) return n.disabledTimeIntervals ? e.extend({}, n.disabledTimeIntervals) : n.disabledTimeIntervals;
        if (!t) return n.disabledTimeIntervals = !1, L(), f;
        if (!(t instanceof Array)) throw new TypeError("disabledTimeIntervals() expects an array parameter");
        return n.disabledTimeIntervals = t, L(), f
      }, f.disabledHours = function(t) {
        if (0 === arguments.length) return n.disabledHours ? e.extend({}, n.disabledHours) : n.disabledHours;
        if (!t) return n.disabledHours = !1, L(), f;
        if (!(t instanceof Array)) throw new TypeError("disabledHours() expects an array parameter");
        if (n.disabledHours = $(t), n.enabledHours = !1, n.useCurrent && !n.keepInvalid) {
          for (var a = 0; !j(r, "h");) {
            if (r.add(1, "h"), 24 === a) throw "Tried 24 times to find a valid date";
            a++
          }
          W(r)
        }
        return L(), f
      }, f.enabledHours = function(t) {
        if (0 === arguments.length) return n.enabledHours ? e.extend({}, n.enabledHours) : n.enabledHours;
        if (!t) return n.enabledHours = !1, L(), f;
        if (!(t instanceof Array)) throw new TypeError("enabledHours() expects an array parameter");
        if (n.enabledHours = $(t), n.disabledHours = !1, n.useCurrent && !n.keepInvalid) {
          for (var a = 0; !j(r, "h");) {
            if (r.add(1, "h"), 24 === a) throw "Tried 24 times to find a valid date";
            a++
          }
          W(r)
        }
        return L(), f
      }, f.viewDate = function(e) {
        if (0 === arguments.length) return i.clone();
        if (!e) return i = r.clone(), f;
        if (!("string" == typeof e || t.isMoment(e) || e instanceof Date)) throw new TypeError("viewDate() parameter must be one of [string, moment or Date]");
        return i = V(e), q(), f
      }, a.is("input")) o = a;
    else if (0 === (o = a.find(n.datepickerInput)).length) o = a.find("input");
    else if (!o.is("input")) throw new Error('CSS class "' + n.datepickerInput + '" cannot be applied to non input element');
    if (a.hasClass("input-group") && (m = 0 === a.find(".datepickerbutton").length ? a.find(".input-group-addon") : a.find(".datepickerbutton")), !n.inline && !o.is("input")) throw new Error("Could not initialize DateTimePicker without an input element");
    return r = M(), i = r.clone(), e.extend(!0, n, (u = {}, (c = a.is("input") || n.inline ? a.data() : a.find("input").data()).dateOptions && c.dateOptions instanceof Object && (u = e.extend(!0, u, c.dateOptions)), e.each(n, function(e) {
      var t = "date" + e.charAt(0).toUpperCase() + e.slice(1);
      void 0 !== c[t] && (u[e] = c[t])
    }), u)), f.options(n), _(), o.on({
      change: K,
      blur: n.debug ? "" : z,
      keydown: G,
      keyup: J,
      focus: n.allowInputToggle ? Q : ""
    }), a.is("input") ? o.on({
      focus: Q
    }) : m && (m.on("click", U), m.on("mousedown", !1)), o.prop("disabled") && f.disable(), o.is("input") && 0 !== o.val().trim().length ? W(V(o.val().trim())) : n.defaultDate && void 0 === o.attr("placeholder") && W(n.defaultDate), n.inline && Q(), f
  };
  return e.fn.datetimepicker = function(t) {
    t = t || {};
    var n, r = Array.prototype.slice.call(arguments, 1),
      i = !0;
    if ("object" == typeof t) return this.each(function() {
      var n, r = e(this);
      r.data("DateTimePicker") || (n = e.extend(!0, {}, e.fn.datetimepicker.defaults, t), r.data("DateTimePicker", a(r, n)))
    });
    if ("string" == typeof t) return this.each(function() {
      var a = e(this).data("DateTimePicker");
      if (!a) throw new Error('bootstrap-datetimepicker("' + t + '") method was called on an element that is not using DateTimePicker');
      n = a[t].apply(a, r), i = n === a
    }), i || e.inArray(t, ["destroy", "hide", "show", "toggle"]) > -1 ? this : n;
    throw new TypeError("Invalid arguments for DateTimePicker: " + t)
  }, e.fn.datetimepicker.defaults = {
    timeZone: "",
    format: !1,
    dayViewHeaderFormat: "MMMM YYYY",
    extraFormats: !1,
    stepping: 1,
    minDate: !1,
    maxDate: !1,
    useCurrent: !0,
    collapse: !0,
    locale: t.locale(),
    defaultDate: !1,
    disabledDates: !1,
    enabledDates: !1,
    icons: {
      time: "glyphicon glyphicon-time",
      date: "glyphicon glyphicon-calendar",
      up: "glyphicon glyphicon-chevron-up",
      down: "glyphicon glyphicon-chevron-down",
      previous: "glyphicon glyphicon-chevron-left",
      next: "glyphicon glyphicon-chevron-right",
      today: "glyphicon glyphicon-screenshot",
      clear: "glyphicon glyphicon-trash",
      close: "glyphicon glyphicon-remove"
    },
    tooltips: {
      today: "Go to today",
      clear: "Clear selection",
      close: "Close the picker",
      selectMonth: "Select Month",
      prevMonth: "Previous Month",
      nextMonth: "Next Month",
      selectYear: "Select Year",
      prevYear: "Previous Year",
      nextYear: "Next Year",
      selectDecade: "Select Decade",
      prevDecade: "Previous Decade",
      nextDecade: "Next Decade",
      prevCentury: "Previous Century",
      nextCentury: "Next Century",
      pickHour: "Pick Hour",
      incrementHour: "Increment Hour",
      decrementHour: "Decrement Hour",
      pickMinute: "Pick Minute",
      incrementMinute: "Increment Minute",
      decrementMinute: "Decrement Minute",
      pickSecond: "Pick Second",
      incrementSecond: "Increment Second",
      decrementSecond: "Decrement Second",
      togglePeriod: "Toggle Period",
      selectTime: "Select Time"
    },
    useStrict: !1,
    sideBySide: !1,
    daysOfWeekDisabled: !1,
    calendarWeeks: !1,
    viewMode: "days",
    toolbarPlacement: "default",
    showTodayButton: !1,
    showClear: !1,
    showClose: !1,
    widgetPositioning: {
      horizontal: "auto",
      vertical: "auto"
    },
    widgetParent: null,
    ignoreReadonly: !1,
    keepOpen: !1,
    focusOnShow: !0,
    inline: !1,
    keepInvalid: !1,
    datepickerInput: ".datepickerinput",
    keyBinds: {
      up: function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") ? this.date(t.clone().subtract(7, "d")) : this.date(t.clone().add(this.stepping(), "m"))
        }
      },
      down: function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") ? this.date(t.clone().add(7, "d")) : this.date(t.clone().subtract(this.stepping(), "m"))
        } else this.show()
      },
      "control up": function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") ? this.date(t.clone().subtract(1, "y")) : this.date(t.clone().add(1, "h"))
        }
      },
      "control down": function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") ? this.date(t.clone().add(1, "y")) : this.date(t.clone().subtract(1, "h"))
        }
      },
      left: function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") && this.date(t.clone().subtract(1, "d"))
        }
      },
      right: function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") && this.date(t.clone().add(1, "d"))
        }
      },
      pageUp: function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") && this.date(t.clone().subtract(1, "M"))
        }
      },
      pageDown: function(e) {
        if (e) {
          var t = this.date() || this.getMoment();
          e.find(".datepicker").is(":visible") && this.date(t.clone().add(1, "M"))
        }
      },
      enter: function() {
        this.hide()
      },
      escape: function() {
        this.hide()
      },
      "control space": function(e) {
        e && e.find(".timepicker").is(":visible") && e.find('.btn[data-action="togglePeriod"]').click()
      },
      t: function() {
        this.date(this.getMoment())
      },
      delete: function() {
        this.clear()
      }
    },
    debug: !1,
    allowInputToggle: !1,
    disabledTimeIntervals: !1,
    disabledHours: !1,
    enabledHours: !1,
    viewDate: !1
  }, e.fn.datetimepicker
});