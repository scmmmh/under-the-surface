var gulp = require('gulp'),
    sass = require('gulp-sass'),
    //autoprefixer = require('gulp-autoprefixer'),
    concat = require('gulp-concat'),
    pump = require('pump');

// Compile the CSS
gulp.task('styles', function(cb) {
    pump([
        gulp.src('styles/theme.scss'),
        sass({
            includePaths: [
                'node_modules/foundation-sites/scss',
                'node_modules/tippy.js/dist',
                'node_modules'
            ]
        }),
        /*autoprefixer({
            browsers: ['last 2 versions'],
            cascade: false
        }),*/
        gulp.dest('theme/static/css')
    ], cb);
});

gulp.task('scripts', function(cb) {
    pump([
        gulp.src([
            'node_modules/what-input/dist/what-input.min.js',
            'node_modules/jquery/dist/jquery.min.js',
            'node_modules/foundation-sites/dist/js/plugins/foundation.core.min.js',
            'node_modules/foundation-sites/dist/js/plugins/foundation.util.keyboard.min.js',
            'node_modules/foundation-sites/dist/js/plugins/foundation.util.box.min.js',
            'node_modules/foundation-sites/dist/js/plugins/foundation.util.nest.min.js',
            'node_modules/foundation-sites/dist/js/plugins/foundation.dropdownMenu.min.js',
            'node_modules/popper.js/dist/umd/popper.min.js',
            'node_modules/tippy.js/dist/tippy.iife.min.js',
            'js/app.js'
        ]),
        concat('app.js'),
        gulp.dest('theme/static/js')
    ], cb);
});

// Generic tasks
gulp.task('default', gulp.parallel('styles', 'scripts'));

gulp.task('watch', gulp.series('default', function(cb) {
    gulp.watch('styles/*.*', gulp.series('styles'));
    gulp.watch('js/**/*.*', gulp.series('scripts'));
    cb();
}));
