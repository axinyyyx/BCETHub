(function () {
    function initGoogleGlowBorder() {
        const elements = document.querySelectorAll(
            ".google-glow-border"
        );

        let activeElement = null;

        elements.forEach(function (element) {
            if (
                element.dataset.googleGlowInitialized === "true"
            ) {
                return;
            }

            element.dataset.googleGlowInitialized = "true";

            let targetAngle = 0;
            let currentAngle = 0;

            let animationFrame = null;

            let isPointerInside = false;
            let isLocked = false;
            let ignoreNextClick = false;

            function normalizeAngle(angle) {
                angle %= 360;

                if (angle < 0) {
                    angle += 360;
                }

                return angle;
            }

            function shortestAngleDifference(from, to) {
                return ((to - from + 540) % 360) - 180;
            }

            function updateAngle(event) {
                const rect =
                    element.getBoundingClientRect();

                const x =
                    event.clientX - rect.left;

                const y =
                    event.clientY - rect.top;

                const centerX =
                    rect.width / 2;

                const centerY =
                    rect.height / 2;

                const angle =
                    Math.atan2(
                        y - centerY,
                        x - centerX
                    ) *
                    (180 / Math.PI);

                targetAngle =
                    normalizeAngle(angle + 90);
            }

            function animate() {
                const difference =
                    shortestAngleDifference(
                        currentAngle,
                        targetAngle
                    );

                currentAngle +=
                    difference * 0.14;

                element.style.setProperty(
                    "--glow-angle",
                    currentAngle + "deg"
                );

                if (
                    Math.abs(difference) > 0.05 &&
                    (isPointerInside || isLocked)
                ) {
                    animationFrame =
                        requestAnimationFrame(
                            animate
                        );
                } else {
                    currentAngle =
                        targetAngle;

                    element.style.setProperty(
                        "--glow-angle",
                        currentAngle + "deg"
                    );

                    animationFrame = null;
                }
            }

            function startAnimation() {
                if (!animationFrame) {
                    animationFrame =
                        requestAnimationFrame(
                            animate
                        );
                }
            }

            function stopAnimation() {
                if (animationFrame) {
                    cancelAnimationFrame(
                        animationFrame
                    );

                    animationFrame = null;
                }
            }

            function showGlow() {
                element.classList.add(
                    "is-glowing"
                );
            }

            function hideGlow() {
                if (!isLocked) {
                    element.classList.remove(
                        "is-glowing"
                    );
                }
            }

            function unlockElement() {
                isLocked = false;

                element.classList.remove(
                    "is-locked",
                    "is-glowing"
                );

                if (activeElement === element) {
                    activeElement = null;
                }

                if (!isPointerInside) {
                    stopAnimation();
                }
            }

            function lockElement(event) {
                if (
                    activeElement &&
                    activeElement !== element
                ) {
                    activeElement.dispatchEvent(
                        new CustomEvent(
                            "google-glow-unlock"
                        )
                    );
                }

                if (isLocked) {
                    unlockElement();
                    return;
                }

                updateAngle(event);

                isLocked = true;

                activeElement = element;

                showGlow();

                element.classList.add(
                    "is-locked"
                );

                startAnimation();
            }

            element.addEventListener(
                "google-glow-unlock",
                function () {
                    isLocked = false;

                    element.classList.remove(
                        "is-locked",
                        "is-glowing"
                    );

                    if (!isPointerInside) {
                        stopAnimation();
                    }
                }
            );

            element.addEventListener(
                "pointerenter",
                function (event) {
                    if (
                        event.pointerType === "touch"
                    ) {
                        return;
                    }

                    isPointerInside = true;

                    updateAngle(event);

                    showGlow();

                    startAnimation();
                }
            );

            element.addEventListener(
                "pointermove",
                function (event) {
                    if (
                        event.pointerType === "touch"
                    ) {
                        return;
                    }

                    isPointerInside = true;

                    updateAngle(event);

                    showGlow();

                    startAnimation();
                }
            );

            element.addEventListener(
                "pointerleave",
                function (event) {
                    if (
                        event.pointerType === "touch"
                    ) {
                        return;
                    }

                    isPointerInside = false;

                    if (!isLocked) {
                        hideGlow();
                        stopAnimation();
                    }
                }
            );

            element.addEventListener(
                "pointerdown",
                function (event) {
                    if (
                        event.pointerType !== "touch"
                    ) {
                        return;
                    }

                    updateAngle(event);

                    isPointerInside = true;

                    if (
                        activeElement &&
                        activeElement !== element
                    ) {
                        activeElement.dispatchEvent(
                            new CustomEvent(
                                "google-glow-unlock"
                            )
                        );
                    }

                    if (isLocked) {
                        unlockElement();

                        ignoreNextClick = true;

                        setTimeout(function () {
                            ignoreNextClick = false;
                        }, 500);

                        return;
                    }

                    isLocked = true;

                    activeElement = element;

                    showGlow();

                    element.classList.add(
                        "is-locked"
                    );

                    startAnimation();

                    ignoreNextClick = true;

                    setTimeout(function () {
                        ignoreNextClick = false;
                    }, 500);
                }
            );

            element.addEventListener(
                "pointercancel",
                function (event) {
                    if (
                        event.pointerType !== "touch"
                    ) {
                        return;
                    }

                    isPointerInside = false;

                    if (!isLocked) {
                        hideGlow();
                        stopAnimation();
                    }
                }
            );

            element.addEventListener(
                "click",
                function (event) {
                    if (ignoreNextClick) {
                        ignoreNextClick = false;
                        return;
                    }

                    if (
                        event.target.closest(
                            "a, button"
                        ) &&
                        !element.matches(
                            "a, button"
                        )
                    ) {
                        return;
                    }

                    lockElement(event);
                }
            );
        });

        document.addEventListener(
            "click",
            function (event) {
                if (!activeElement) {
                    return;
                }

                if (
                    !event.target.closest(
                        ".google-glow-border"
                    )
                ) {
                    activeElement.dispatchEvent(
                        new CustomEvent(
                            "google-glow-unlock"
                        )
                    );

                    activeElement = null;
                }
            },
            true
        );
    }

    if (
        document.readyState === "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            initGoogleGlowBorder
        );
    } else {
        initGoogleGlowBorder();
    }
})();