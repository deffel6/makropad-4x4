/*
 * Blaue LED des nice!nano (P0.15) als Tastenanzeige.
 *
 * Ab Werk blinkt die LED dauerhaft. Dieses Modul nimmt sie in Besitz:
 * beim Start wird sie ausgeschaltet, und jeder Tastendruck laesst sie
 * kurz aufleuchten. Losgelassen wird nicht beachtet - sonst wuerde die
 * LED bei langem Halten zweimal blitzen.
 *
 * Die Dauer steht in CONFIG_TASTENDRUCK_LED_MS (Vorgabe 40 ms). Ein
 * einzelner verzoegerter Auftrag genuegt: Kommt waehrend des Leuchtens
 * der naechste Tastendruck, verschiebt k_work_reschedule nur dessen
 * Ablaufzeit, statt einen zweiten Auftrag anzulegen.
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/init.h>

#include <zmk/event_manager.h>
#include <zmk/events/position_state_changed.h>

static const struct gpio_dt_spec tasten_led =
	GPIO_DT_SPEC_GET(DT_NODELABEL(led_tastendruck), gpios);

static void led_aus(struct k_work *work)
{
	ARG_UNUSED(work);
	gpio_pin_set_dt(&tasten_led, 0);
}

static K_WORK_DELAYABLE_DEFINE(led_aus_auftrag, led_aus);

static int tastendruck_beobachter(const zmk_event_t *eh)
{
	const struct zmk_position_state_changed *ev = as_zmk_position_state_changed(eh);

	if (ev != NULL && ev->state) {
		gpio_pin_set_dt(&tasten_led, 1);
		k_work_reschedule(&led_aus_auftrag, K_MSEC(CONFIG_TASTENDRUCK_LED_MS));
	}

	/* Das Ereignis muss weiterlaufen, sonst kommt kein Tastendruck an. */
	return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(tastendruck_led, tastendruck_beobachter);
ZMK_SUBSCRIPTION(tastendruck_led, zmk_position_state_changed);

static int tastendruck_led_init(void)
{
	if (!gpio_is_ready_dt(&tasten_led)) {
		return -ENODEV;
	}

	/* INACTIVE = aus. Damit ist das Blinken ab dem Start weg. */
	return gpio_pin_configure_dt(&tasten_led, GPIO_OUTPUT_INACTIVE);
}

SYS_INIT(tastendruck_led_init, APPLICATION, CONFIG_APPLICATION_INIT_PRIORITY);
