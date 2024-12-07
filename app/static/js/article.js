const errorImgSrc = "https://media.tenor.com/1UgbfxIH5ywAAAAM/11.gif";

$(document).ready(function () {
  const $cover = $("#cover");

  $cover.keyup(function () {
    const val = $cover.val();
    if (!val.trim().length) {
      $("#photo").attr("src", errorImgSrc);
      return;
    }

    $("#photo").attr("src", val);
  });
});

function imageError() {
  console.log("Error");
  $("#photo").attr("src", errorImgSrc);
}
