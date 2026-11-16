/* Medição do Google Ads: conversão "Clique no WhatsApp".
   Preencha ID (ex.: "AW-123456789") e ROTULO (o rótulo da conversão) quando a
   conversão for criada no Google Ads. Enquanto ID estiver vazio, nada é carregado. */
(function () {
  var ID = "";
  var ROTULO = "";
  if (!ID) return;
  var CONVERSAO = ID + "/" + ROTULO;

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  window.gtag("config", ID);

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (href.indexOf("https://wa.me/") !== 0 && href.indexOf("https://api.whatsapp.com/") !== 0) return;
    if (ROTULO) window.gtag("event", "conversion", { send_to: CONVERSAO });
  }, true);
})();
