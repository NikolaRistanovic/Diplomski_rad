#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "driver/mcpwm_prelude.h"
#include <driver/gptimer.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "soc/soc_caps.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
//Inspiration code : https://github.com/espressif/esp-idf/blob/v6.1/examples/peripherals/adc/oneshot_read/main/oneshot_read_main.c
//Inspo 2 https://github.com/espressif/esp-idf/blob/v6.1/examples/peripherals/mcpwm/mcpwm_servo_control/main/mcpwm_servo_control_example_main.c


const static char *TAG = "EXAMPLE";


#define SERVO_PULSE_GPIO             5        // GPIO connects to the PWM signal line
#define SERVO_TIMEBASE_RESOLUTION_HZ 1000000  // 1MHz, 1us per tick
#define SERVO_TIMEBASE_PERIOD        2000    // 20000 ticks, 20ms


#define CH1_GPIO 3

int adc_raw;

//ADC Config
static adc_channel_t ADC_CH_NO;
static adc_unit_t ADC_UNIT_NO = ADC_UNIT_1;

adc_oneshot_unit_handle_t adc1_handle;
adc_oneshot_unit_init_cfg_t init_config1 = {
    .unit_id = ADC_UNIT_1};

adc_oneshot_chan_cfg_t config = {
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_12};

//PWM config
//Timer Config
mcpwm_timer_handle_t timer = NULL;
mcpwm_timer_config_t timer_config = {
    .group_id = 0,
    .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
    .resolution_hz = SERVO_TIMEBASE_RESOLUTION_HZ,
    .period_ticks = SERVO_TIMEBASE_PERIOD,
    .count_mode = MCPWM_TIMER_COUNT_MODE_UP};

//Operator Config
mcpwm_oper_handle_t oper = NULL;
mcpwm_operator_config_t operator_config = {
    .group_id = 0}; // operator must be in the same group to the timer

//Comparator Config
mcpwm_cmpr_handle_t comparator = NULL;
mcpwm_comparator_config_t comparator_config = {
    .flags.update_cmp_on_tez = true};

//Generator Config
mcpwm_gen_handle_t generator = NULL;
mcpwm_generator_config_t generator_config = {
    .gen_gpio_num = SERVO_PULSE_GPIO};

void app_main(void)
{

    //-------------ADC1 Config---------------//
    ESP_ERROR_CHECK(adc_oneshot_io_to_channel(3,&ADC_UNIT_NO,&ADC_CH_NO));
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config1, &adc1_handle));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, ADC_CH_NO, &config));
    ESP_LOGI(TAG, "Finished setting up ADC");

    //-------------MCPWM Config---------------//
    //Create timer
    ESP_ERROR_CHECK(mcpwm_new_timer(&timer_config, &timer));

    //Create and connect operator
    ESP_ERROR_CHECK(mcpwm_new_operator(&operator_config, &oper));
    ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

    //Create Comparator and generator
    ESP_ERROR_CHECK(mcpwm_new_comparator(oper, &comparator_config, &comparator));
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &generator_config, &generator));

    //Set the initial compare value
    ESP_ERROR_CHECK(mcpwm_comparator_set_compare_value(comparator, 0));
    //Go high on counter empty
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(
        generator,MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
    //Go low on compare threshold
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(
        generator,MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, comparator, MCPWM_GEN_ACTION_LOW)));

    ESP_LOGI(TAG, "Enable and start timer");
    ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
    ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));
    //Enable timer and start complete



    while (1) {
        ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, ADC_CH_NO, &adc_raw));
        ESP_LOGI(TAG, "ADC%d Channel[%d] Raw Data: %d", ADC_UNIT_1 + 1, ADC_CH_NO, adc_raw);

        ESP_ERROR_CHECK(mcpwm_comparator_set_compare_value(comparator, SERVO_TIMEBASE_PERIOD*adc_raw/4095));
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    ESP_ERROR_CHECK(adc_oneshot_del_unit(adc1_handle));

}
