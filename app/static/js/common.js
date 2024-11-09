$(document).ready(function () {
  const $starRating = $(".star-rating");
  let $alreadyActiveStars;

  $starRating.on("mouseover", function () {
    const $stars = $(this).find(".star-rating__star");

    $stars.on("mouseover", function () {
      const $thisStar = $(this);
      const starIndex = $thisStar.index();

      if (!$alreadyActiveStars) {
        $alreadyActiveStars = $stars.filter(
          ".star-rating__star.text-yellow-300"
        );
      }

      const $activeStars = $stars.slice(0, starIndex + 1);
      const $inactiveStars = $stars.slice(starIndex + 1);
      $activeStars.each(function () {
        activateStar($(this));
      });
      $inactiveStars.each(function () {
        deactivateStar($(this));
      });
    });
  });

  $starRating.on("mouseleave", function () {
    if (!$alreadyActiveStars) return;

    const $stars = $(this).find(".star-rating__star");
    $stars.each(function () {
      deactivateStar($(this));
    });
    $alreadyActiveStars.each(function () {
      activateStar($(this));
    });

    $alreadyActiveStars = undefined;
  });
});

const deactivateStar = ($star) => {
  if ($star.hasClass("text-yellow-300")) {
    $star.removeClass("text-yellow-300");
  }
  if (!$star.hasClass("text-gray-200")) {
    $star.addClass("text-gray-200");
  }
  if (!$star.hasClass("dark:text-gray-600")) {
    $star.addClass("dark:text-gray-600");
  }
};

const activateStar = ($star) => {
  if (!$star.hasClass("text-yellow-300")) {
    $star.addClass("text-yellow-300");
  }
  if ($star.hasClass("text-gray-200")) {
    $star.removeClass("text-gray-200");
  }
  if ($star.hasClass("dark:text-gray-600")) {
    $star.removeClass("dark:text-gray-600");
  }
};
